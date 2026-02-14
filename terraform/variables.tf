variable "gcp_project_id" {
  description = "The GCP project ID."
}

variable "gcp_region" {
  description = "The GCP region."
}

variable "api_services" {
  type = list(string)
  default = [
    "pubsub.googleapis.com"
  ]
}