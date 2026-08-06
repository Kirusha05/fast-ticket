# --- GitHub deployer service account
resource "google_service_account" "deployer_sa" {
  account_id   = "github-deployer"
  display_name = "GitHub deployer service account"
  description  = "Service account used inside GitHub actions during CI/CD for app updates"
}

# --- Terraform runner service account
resource "google_service_account" "terraform_runner_sa" {
  account_id   = "terraform-runner"
  display_name = "Terraform runner service account"
  description  = "Service account used inside GitHub actions during CD for applying infra updates"
}

# gets roles/owner (roles/editor can't manage IAM bindings)
resource "google_project_iam_member" "terraform_runner_editor" {
  project = var.project_id
  role    = "roles/owner"
  member  = "serviceAccount:${google_service_account.terraform_runner_sa.email}"

  depends_on = [google_service_account.terraform_runner_sa]
}

# --- Terraform planner
resource "google_service_account" "terraform_planner_sa" {
  account_id   = "terraform-planner"
  display_name = "Terraform planner service account"
  description  = "Service account used inside GitHub actions during CI (PRs) for viewing planned infra updates"
}

# gets roles/viewer (only needs to view the GCP state)
resource "google_project_iam_member" "terraform_planner_viewer" {
  project = var.project_id
  role    = "roles/viewer"
  member  = "serviceAccount:${google_service_account.terraform_planner_sa.email}"

  depends_on = [google_service_account.terraform_planner_sa]
}

# and roles/storage.objectAdmin on the state bucket (terraform plan needs to read state and write the lock)
# roles/storage.objectAdmin grants full read/write/delete on objects in that bucket,
# but there's no narrower predefined role that separates "read state" from "manage lock", so we'll keep it like this for now
resource "google_storage_bucket_iam_member" "terraform_planner_state_admin" {
  bucket = google_storage_bucket.terraform_state.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.terraform_planner_sa.email}"

  depends_on = [google_service_account.terraform_planner_sa]
}

# These get the IAM bindings for connecting to GCP through Workload Identity Federation inside wif.tf
