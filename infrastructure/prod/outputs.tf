output "artifact_registry_url" {
  value = google_artifact_registry_repository.app_repo.registry_uri
}

output "frontend_cloud_run_uri" {
  value = google_cloud_run_v2_service.frontend_service.uri
}

output "backend_cloud_run_uri" {
  value = google_cloud_run_v2_service.backend_service.uri
}