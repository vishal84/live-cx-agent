terraform {
  backend "gcs" {
    bucket = "kpmg-agents-tf-state"
    prefix = "live-cx-agent" # folder under bucket for workload..
  }
}