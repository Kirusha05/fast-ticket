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
