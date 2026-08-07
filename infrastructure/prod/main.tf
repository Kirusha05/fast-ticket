# --- Artifact Registry repo
resource "google_artifact_registry_repository" "app_repo" { # the local Terraform resource name
  project       = var.project_id
  location      = var.region
  repository_id = "fast-ticket-repo" # the actual resource id created inside GCP
  format        = "Docker"
  description   = "Docker repo for FastTicket app images"

  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"
    most_recent_versions {
      keep_count = 10
    }
  }
}


# --- GitHub deployer SA (created during initial bootstrap) IAM bindings
# it should be allowed to push to the app's artifact registry (granular, not all the project repos)
data "google_service_account" "deployer_sa" {
  account_id = "github-deployer"
}

resource "google_artifact_registry_repository_iam_member" "deployer_sa_ar_writer" {
  repository = google_artifact_registry_repository.app_repo.id
  role       = "roles/artifactregistry.writer"
  member     = data.google_service_account.deployer_sa.member
  # equivalent to member  = "serviceAccount:${data.google_service_account.deployer_sa.email}"
}

# and should be allowed to push new revisions to Cloud Run
resource "google_project_iam_member" "deployer_sa_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = data.google_service_account.deployer_sa.member
}


# --- Cloud Run runtime service account; will get the Secret Manager permissions attached in the backend section down below
resource "google_service_account" "runtime_sa" {
  account_id   = "cloud-run-runtime"
  display_name = "Runtime service account"
  description  = "Service account used by Cloud Run apps during runtime"
}

# allow the GitHub deployer SA to use the runtime SA and attach it to the Cloud Run revisions during deployment
# roles/iam.serviceAccountUser: lets a principal attach a service account to a resource it's creating/managing
resource "google_service_account_iam_member" "runtime_sa_user" {
  service_account_id = google_service_account.runtime_sa.id
  role               = "roles/iam.serviceAccountUser"
  member             = data.google_service_account.deployer_sa.member

  depends_on = [google_service_account.runtime_sa]
}


# --- Cloud Run frontend service; created first so we can set CORS_MAIN_ORIGIN = frontend_service.uri for the backend_service
resource "google_cloud_run_v2_service" "frontend_service" {
  name                 = "fast-ticket-frontend"
  location             = var.region
  invoker_iam_disabled = true # allowing public (unauthenticated) access

  # service-level scaling
  scaling {
    min_instance_count = 0
    max_instance_count = 1
  }

  template {
    service_account                  = google_service_account.runtime_sa.email
    max_instance_request_concurrency = 1000
    timeout                          = "30s"

    containers {
      # a dummy public image just so Cloud Run accepts the initial creation
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      ports {
        container_port = 80
      }
      resources {
        startup_cpu_boost = true
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 80
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 80
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }
    }
  }

  # defaults to 100% traffic to the latest Ready Revision
  # traffic {}

  # Without an ignore_changes block, the next terraform apply will revert the container 
  # back to us-docker.pkg.dev/cloudrun/container/hello, undoing whatever was deployed later on by CI/CD
  # Terraform owns everything about the service except the image tag; CI/CD updates just the image tag on each deployment
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      client,
      client_version,
    ]
  }

  # for running this test and detroying later; set to true in prod
  deletion_protection = false
}


# --- Cloud Run backend service env variables setup
# non-sensitive env vars config map and secret env vars mapping to their Secret Manager ids
locals {
  backend_env = {
    MODE = "cloud"

    DB_DATABASE              = "postgres"
    DB_PORT                  = 5432
    DB_POOL_MIN_SIZE         = 10
    DB_POOL_MAX_SIZE         = 60
    DB_POOL_CREATION_TIMEOUT = 5

    AUTH0_AUDIENCE  = "https://fast-ticket.com"
    AUTH0_DOMAIN    = "krrr.eu.auth0.com"
    AUTH0_CLIENT_ID = "l48RZLGylbcQTAJXELwKhDcgCZUBFba0"

    STRIPE_PUBLISHABLE_KEY  = "pk_test_51TtUWeRrQ0c8vI2sCSYeIe0gLVHvRbFEf22mnYFeH8McrHzTrb591yW7yW2N6tU5ELR0ADI2890ELBxlEWyeM5jl00Hdd5s1YP"
    STRIPE_CURRENCY         = "usd"
    STRIPE_SUCCESS_URL_PATH = "/bookings/new/success"
    STRIPE_CANCEL_URL_PATH  = "/bookings"

    BOOKING_RESERVATION_TTL_HOURS = 2
    CORS_MAIN_ORIGIN              = google_cloud_run_v2_service.frontend_service.uri
  }

  # env var name -> Secret Manager secret_id mapping
  backend_secret_env = {
    DB_HOST               = "db-host"
    DB_USER               = "db-user"
    DB_PASSWORD           = "db-password"
    AUTH0_CLIENT_SECRET   = "auth0-client-secret"
    STRIPE_SECRET_KEY     = "stripe-secret-key"
    STRIPE_WEBHOOK_SECRET = "stripe-webhook-secret"
  }
}

# the secret env vars will be stored in Secret Manager and manually set by an admin
resource "google_secret_manager_secret" "backend_secrets" {
  for_each  = local.backend_secret_env
  secret_id = each.value # e.g. "auth0-client-secret"

  replication {
    auto {}
  }
}

# seed an initial (placeholder) version so Cloud Run can reference "latest"
# later on, admins will create a new version for each one with the real secret value
resource "google_secret_manager_secret_version" "backend_secret_seed" {
  for_each    = google_secret_manager_secret.backend_secrets
  secret      = each.value.id
  secret_data = "terraform-initial-placeholder"
}

# Cloud Run runtime SA can read only these secrets, not all the project secrets
resource "google_secret_manager_secret_iam_member" "runtime_sa_secret_access" {
  for_each  = google_secret_manager_secret.backend_secrets
  secret_id = each.value.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime_sa.email}"
}


# --- Cloud Run backend service
resource "google_cloud_run_v2_service" "backend_service" {
  name                 = "fast-ticket-backend"
  location             = var.region
  invoker_iam_disabled = true # allowing public (unauthenticated) access

  # service-level scaling
  scaling {
    min_instance_count = 0
    max_instance_count = 1
  }

  template {
    service_account                  = google_service_account.runtime_sa.email
    max_instance_request_concurrency = 200
    timeout                          = "300s"

    containers {
      # a dummy public image just so Cloud Run accepts the initial creation
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      ports {
        container_port = 8000
      }
      resources {
        startup_cpu_boost = true
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      dynamic "env" {
        for_each = local.backend_env

        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = local.backend_secret_env

        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.backend_secrets[env.key].secret_id
              version = "latest"
            }
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }
    }
  }

  # defaults to 100% traffic to the latest Ready Revision
  # traffic {}

  # Without an ignore_changes block, the next terraform apply will revert the container 
  # back to us-docker.pkg.dev/cloudrun/container/hello, undoing whatever was deployed later on by CI/CD
  # Terraform owns everything about the service except the image tag; CI/CD updates just the image tag on each deployment
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      client,
      client_version,
    ]
  }

  # for running this test and detroying later; set to true in prod
  deletion_protection = false
}
