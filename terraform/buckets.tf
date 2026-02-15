resource "google_storage_bucket" "agent_bucket" {
  name                        = "live-cx-agent"
  location                    = var.gcp_region
  force_destroy               = true
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}

resource "google_storage_bucket" "agent_engine_bucket" {
  name                        = "${var.project_prefix}-agent_engine"
  location                    = var.gcp_region
  force_destroy               = true
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}
