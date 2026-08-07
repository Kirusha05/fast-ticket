# this file should only define the structure (types and descriptions) of the infrastructure
# the actual values will be loaded from .auto.tfvars files
variable "project_id" {
  type = string
}

variable "project_number" {
  type = string
}

variable "region" {
  type = string
}

variable "github_repo" {
  type = string
}
