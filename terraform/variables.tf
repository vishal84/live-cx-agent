variable "gcp_project_id" {
  description = "The GCP project ID."
}

variable "gcp_region" {
  description = "The GCP region."
}

variable "project_prefix" {
  description = "Prefix for project resources"
  type        = string
}

variable "api_services" {
  type = list(string)
  default = [
    "pubsub.googleapis.com"
  ]
}