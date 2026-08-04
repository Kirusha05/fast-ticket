# Artifact Registry repo
resource "google_artifact_registry_repository" "test_repo" { # the local Terraform resource name
  project       = var.project_id
  location      = var.region
  repository_id = "test-app-repo" # the actual resource id created inside GCP
  format        = "Docker"
  description   = "Docker repo for my app"

  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"
    most_recent_versions {
      keep_count = 10
    }
  }

  depends_on = [google_project_service.services]
}

# Secret Manager to store the DB password
resource "google_secret_manager_secret" "test_db_password" {
  depends_on = [google_project_service.services]

  secret_id = "test_db_password"

  replication {
    auto {}
  }
}

# Service Account for Cloud Run
resource "google_service_account" "test_cloud_run_sa" {
  depends_on = [google_project_service.services]

  account_id   = "test-cloud-run-sa"
  display_name = "Service Account for Cloud Run"
}

# Give the SA access to the secret
resource "google_secret_manager_secret_iam_member" "sa_secret_access" {
  depends_on = [google_project_service.services]

  secret_id = google_secret_manager_secret.test_db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.test_cloud_run_sa.email}"
}

# Cloud Run backend service
resource "google_cloud_run_v2_service" "test_backend_service" {
  depends_on = [google_project_service.services]

  name                 = "test-backend"
  location             = var.region
  invoker_iam_disabled = true # allowing public (unauthenticated) access

  # service-level scaling
  scaling {
    min_instance_count = 0
    max_instance_count = 1
  }

  template {
    service_account                  = google_service_account.test_cloud_run_sa.email
    max_instance_request_concurrency = 200

    containers {
      # a dummy public image just so Cloud Run accepts the initial creation
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      resources {
        startup_cpu_boost = true
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
      # liveness_probe {
      #   http_get {
      #     path = "/health"
      #     port = 8000
      #   }
      #   initial_delay_seconds = 10
      #   timeout_seconds = 3
      #   period_seconds = 10
      #   failure_threshold = 3
      # }
      # startup_probe {
      #   http_get {
      #     path = "/health"
      #     port = 8000
      #   }
      #   initial_delay_seconds = 10
      #   timeout_seconds = 3
      #   period_seconds = 10
      #   failure_threshold = 3
      # }
    }

    # # revision-level scaling
    # scaling {
    #   min_instance_count = 0
    #   max_instance_count = 1
    # }
  }

  # defaults to 100% traffic to the latest Ready Revision
  # traffic {}

  # Without an ignore_changes block, the next terraform apply will revert the container 
  # back to us-docker.pkg.dev/cloudrun/container/hello, undoing whatever was deployed later on by CI/CD
  lifecycle {
    ignore_changes = [template[0].containers[0].image]
  }

  # for running this test and detroying later; set to true in prod
  deletion_protection = false
}
