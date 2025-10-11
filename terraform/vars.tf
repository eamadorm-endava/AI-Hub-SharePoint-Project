variable "gcp_project_id" {
  type        = string
  description = "GCP Project ID"
  default     = "p-dev-gce-60pf"
}

variable "gcp_region" {
  type        = string
  description = "Region where the resources will be stored"
  default     = "northamerica-south1"
}


variable "gcp_zone" {
  type        = string
  description = "GCP zone within the gcp_region"
  default     = "northamerica-south1-a"
}

variable "artifact_registry_name" {
  type        = string
  description = "Name of the artifact registry to create"
  default     = "ai-hub-sharepoint"
}

variable "artifact_registry_dry_run" {
  type        = bool
  description = "Determines if cleanup policies delete artifacts. true: No artifacts are deleted. false: Artifacts are deleted or kept depending on the policies"
  default     = false
}
