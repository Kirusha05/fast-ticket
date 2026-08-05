output "terraform_state_gcs_bucket" {
  value = google_storage_bucket.terraform_state.id
}