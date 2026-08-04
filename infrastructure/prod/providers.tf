# configure the Google Cloud provider
# bucket should be set to terraform_state_gcs_bucket output produced by running "terraform apply" in the bootstrap folder
terraform {
  backend "gcs" {
    bucket = "fast-ticket-app-terraform-state"
    prefix = "prod"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.42.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
