# the GCS state bucket to be used as backend for prod/staging terraform setup
output "terraform_state_gcs_bucket" {
  value = google_storage_bucket.terraform_state.id
}

# represents the WIF_PROVIDER env var used by GitHub Actions
output "workload_identity_pool_provider" {
  value = google_iam_workload_identity_pool_provider.github_provider.name
}