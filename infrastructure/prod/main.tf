# --- Artifact Registry rep
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

  depends_on = [google_project_service.services]
}


# --- GitHub deployer service account
resource "google_service_account" "deployer_sa" {
  account_id   = "github-deployer"
  display_name = "GitHub deployer service account"
  description  = "Service account used inside GitHub actions during CI/CD"

  depends_on = [google_project_service.services]
}

# it should be allowed to push to the app's artifact registry (granular, not all the project repos)
resource "google_artifact_registry_repository_iam_member" "depoyer_sa_permissions" {
  repository = google_artifact_registry_repository.app_repo.id
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.deployer_sa.email}"

  depends_on = [google_service_account.deployer_sa]
}

# and should be allowed to control Cloud Run resources
resource "google_project_iam_member" "depoyer_sa_permissions" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.deployer_sa.email}"

  depends_on = [google_service_account.deployer_sa]
}


# --- Cloud Run runtime service account; no roles attached for now, just a separate empty SA
resource "google_service_account" "runtime_sa" {
  account_id   = "cloud-run-runtim"
  display_name = "Runtime service account"
  description  = "Service account used by Cloud Run apps during runtime"

  depends_on = [google_project_service.services]
}

# allow the GitHub deployer SA to use the runtime SA and attach it to the Cloud Run revisions during deployment
# roles/iam.serviceAccountUser: lets a principal attach a service account to a resource it's creating/managing
resource "google_service_account_iam_member" "runtime_sa_user" {
  service_account_id = google_service_account.runtime_sa.id
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.deployer_sa.email}"

  depends_on = [google_service_account.deployer_sa, google_service_account.runtime_sa]
}

# --- Setting up Workload Identity Federation
# create the workload identity pool
# wtf is a pool? from GCloud Web Console:
# "Create a pool for each environment that needs access to Google Cloud resources"
# so GitHub Actions (or GitLab CI, or a Kubernetes Cluster) will be one of these environments
# "environment" means an external identity environment, not a deployment environment like development/staging/production.
# The Workload Identity Pool is where you tell Google Cloud: "I trust identities coming from this external environment."
resource "google_iam_workload_identity_pool" "wif_github_pool" {
  workload_identity_pool_id = "github-identity-pool"
  display_name              = "GitHub Actions identity pool"
}

# One pool can contain multiple providers.
# Workload Identity Pool
# ├── Provider for your personal GitHub account
# ├── Provider for your company's GitHub organization
# └── Provider for another GitHub Enterprise instance
# The provider defines how to validate the incoming identity tokens (issuer, attribute mapping, etc.)

# Despite it being named "provider", it doesn't provide anything, no authentication, no credentials, nothing like that
# A "provider" is just a weird name for a "configuration". That's all. It just says "When someone gives me a token 
# whose issuer is https://token.actions.githubusercontent.com, here's how to validate it."
# But we could also say that Github is the Identity Provider, providing the JWT that mentions the repo, the branch, the actor.
# Github provides this information and Google validates it. Github creates a signed OIDC JWT that looks like this:
# {
#   "iss": "https://token.actions.githubusercontent.com",
#   "sub": "repo:Kirusha05/ticket-app:ref:refs/heads/main",
#   "repository": "Kirusha05/ticket-app",
#   "repository_owner": "Kirusha05",
#   "actor": "Kirusha05",
#   "ref": "refs/heads/main",
#   "sha": "8c7c0d..."
# }

# create the Github provider, telling Google that this pool trusts GitHub
# and will successfully authorize the identities from the repository and branch set in attribute_condition
# attribute_condition is evaluated at token-exchange time, before Google even issues a federated token. 
# If the incoming assertion doesn't satisfy the CEL expression, the exchange fails outright with a permission-denied error
# and google-github-actions/auth fails before it ever gets to the impersonation step

# attribute_mapping sets multiple attributes:
# - google.subject = assertion.sub (repo:Kirusha05/ticket-app:ref:refs/heads/main), required by google identity
# (every authenticated identity needs one canonical identifier)
# - attribute.repository=assertion.repository (the source repo), used later on for IAM bindings to the service account
resource "google_iam_workload_identity_pool_provider" "wif_github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.wif_github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "main-branch-provider"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_condition = "assertion.repository == '${var.github_repo}' && assertion.ref == 'refs/heads/main'"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }

  depends_on = [google_iam_workload_identity_pool.wif_github_pool]
}

# the generated provider name (projects/123456789012/locations/global/workloadIdentityPools/gh-pool/providers/gh-provider)
# will be the WIF_PROVIDER env var used by google-github-actions/auth
# This value just tells Google Cloud "when validating a token, use this specific pool+provider configuration to check it."

# allow impersonation
# roles/iam.workloadIdentityUser: lets an external identity (from a WIF pool) impersonate the service account 
# by exchanging its federated token for a short-lived access token of that SA.
# "attribute.repository/${var.github_repo}" uses the exact attribute we've set in the provider's attribute_mapping
resource "google_service_account_iam_member" "workload_identity_impersonation" {
  service_account_id = google_service_account.deployer_sa.id
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/projects/${var.project_number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.wif_github_pool.workload_identity_pool_id}/attribute.repository/${var.github_repo}"

  depends_on = [google_iam_workload_identity_pool.wif_github_pool]
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
    }
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
  depends_on          = [google_project_service.services]
}


# --- Cloud Run frontend service
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
    }
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
  depends_on          = [google_project_service.services]
}
