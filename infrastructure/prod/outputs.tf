output "artifact_registry_url" {
  value = google_artifact_registry_repository.test_repo.registry_uri
}

output "cloud_run_uri" {
  value = google_cloud_run_v2_service.test_backend_service.uri
}

output "cloud_run_urls" {
  value = google_cloud_run_v2_service.test_backend_service.urls
}
