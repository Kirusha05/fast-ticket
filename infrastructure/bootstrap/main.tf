# this will create the GCS bucket that will serve as the backend for the main Terraform state, shared by the team
# will be applied only once in the project lifetime, before the initial infra provisioning

resource "google_storage_bucket" "terraform_state" {
  name     = "${var.project_id}-terraform-state"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  # rule 1: keep at most the 10 most recent versions of each object
  lifecycle_rule {
    action {
      type = "Delete"
    }

    condition {
      num_newer_versions = 10
    }
  }

  # rule 2: delete noncurrent/archived versions once they're older than 90 days
  lifecycle_rule {
    action {
      type = "Delete"
    }

    condition {
      days_since_noncurrent_time = 90
      with_state                 = "ARCHIVED"
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

# # and a service account that will run "terraform apply" or access the outputs inside the CI/CD pipeline
# resource "google_service_account" "terraform_ci" {
#   account_id   = "terraform-ci-cd"
#   display_name = "Terraform CI/CD (GitHub Actions)"
#   description  = "Used by GitHub Actions to plan/apply Terraform changes"
# }

# # allow reading/writing the state bucket
# resource "google_storage_bucket_iam_member" "terraform_ci_state_access" {
#   bucket = google_storage_bucket.terraform_state.name
#   role   = "roles/storage.objectAdmin"
#   member = "serviceAccount:${google_service_account.terraform_ci.email}"
# }