# --- Setting up Workload Identity Federation
# detailed explanation inside wif.explained.txt
resource "random_id" "pool_suffix" {
  byte_length = 4
}

resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-identity-pool-${random_id.pool_suffix.hex}"
  display_name              = "GitHub Actions identity pool"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  # allow just the identities coming from our repo
  attribute_condition = "assertion.repository == '${var.github_repo}'"
  # and save a few fields for further IAM bindings
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  depends_on = [google_iam_workload_identity_pool.github_pool]
}

# --- Allow impersonation, so GitHub actions can run as the defined Service Accounts
locals {
  pool_id = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  base    = "principalSet://iam.googleapis.com/projects/${var.project_number}/locations/global/workloadIdentityPools/${local.pool_id}"
  main_branch    = "${local.base}/attribute.ref/refs/heads/main"
  our_repo    = "${local.base}/attribute.repository/${var.github_repo}"
}

# image push + cloud run deploy: main only
resource "google_service_account_iam_member" "deployer_wif" {
  service_account_id = google_service_account.deployer_sa.id
  role               = "roles/iam.workloadIdentityUser"
  member             = local.main_branch
}

# terraform apply: main branch only
resource "google_service_account_iam_member" "runner_wif" {
  service_account_id = google_service_account.terraform_runner_sa.id
  role               = "roles/iam.workloadIdentityUser"
  member             = local.main_branch
}

# terraform plan: any branch in this repo
resource "google_service_account_iam_member" "planner_wif" {
  service_account_id = google_service_account.terraform_planner_sa.id
  role               = "roles/iam.workloadIdentityUser"
  member             = local.our_repo
}

# GitHub actions jobs will request to act as their needed service account through WIF
# and will get access to that service account only if the request come from our repo:
# pool provider's attribute_condition = "assertion.repository == '${var.github_repo}'"
# and the request was made from the desired branches (member = local.main_branch) or any (member = local.our_repo)