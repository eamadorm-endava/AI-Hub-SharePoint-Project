provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}


############### ARTIFACT REGISTRY ###############
resource "google_artifact_registry_repository" "ai-hub-sharepoint" {
  location               = var.gcp_region
  repository_id          = var.artifact_registry_name
  format                 = "docker"
  cleanup_policy_dry_run = var.artifact_registry_dry_run
  cleanup_policies {
    id     = "delete_untagged_images"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "3d" # after 3 days untagged, delete the image 
    }
  }
  # Check documentation for vulnerability scanning
  # https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/artifact_registry_repository.html#nested_vulnerability_scanning_config
  vulnerability_scanning_config {
    enablement_config = "DISABLED"
  }
}
