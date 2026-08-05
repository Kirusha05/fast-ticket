# configure the Google Cloud provider
terraform {
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