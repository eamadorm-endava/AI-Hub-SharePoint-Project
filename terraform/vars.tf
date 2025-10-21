variable "gcp_project_id" {
  type        = string
  description = "GCP Project ID"
  default     = "p-dev-gce-60pf"
}

variable "gcp_dev_sa" {
  type        = string
  description = "GCP Service Account that CloudRun will use to authenticate"
  default     = "dev-service-account@p-dev-gce-60pf.iam.gserviceaccount.com"
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

variable "main_bucket_name" {
  type        = string
  description = "Name of the main GCS bucket to store blobs"
  default     = "ai-hub-sharepoint"
}

variable "main_bucket_storage_class" {
  type        = string
  description = "Storage class of the main GCS bucket"
  default     = "STANDARD"
}

variable "main_bucket_autoclass_enabled" {
  type        = bool
  description = "Determines if Autoclass is enabled for the main GCS bucket"
  default     = true
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

variable "news_extraction_pipeline_instance" {
  type        = string
  description = "Name of the CloudRun service that executes the news extraction pipeline"
  default     = "news-extraction-pipeline" # only lower-case, digits, and hyphens
}

variable "news_extraction_pipeline_port" {
  type        = number
  description = "Port where the CloudRun service will listen"
  default     = 8000
}

variable "news_extraction_pipeline_image_name" {
  type        = string
  description = "Name of the docker image that contains the news extraction pipeline"
  default     = "news_extraction_pipeline"
}

variable "news_extraction_pipeline_image_tag" {
  type        = string
  description = "Tag of the docker image that contains the news extraction pipeline"
  default     = "latest"
}

variable "dataset_id" {
  type        = string
  description = "ID of the dataset that the AI agent will have access to"
  default     = "ai_hub_sharepoint"
}

variable "news_metadata_table_id" {
  type        = string
  description = "ID of the table ai_news_metadata"
  default     = "news_metadata"
}
