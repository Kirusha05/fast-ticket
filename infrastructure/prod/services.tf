# enables the required GCloud APIs
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com", # used for Workload Identity Federation
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}
