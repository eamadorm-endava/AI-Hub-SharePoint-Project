variable "azure_subscription_id" {
  type        = string
  description = "Azure subscription ID where the resources will be created."
  default     = "15158422-ef98-425f-a0e3-6e53c81ba478"
}

variable "tag_owner" {
  type        = string
  description = "Value of the tag 'Owner'"
  default     = "Emmanuel_Amador"
}

variable "tag_tower" {
  type        = string
  description = "Value of the tag 'Tower'"
  default     = "Infrastructure"
}

variable "tag_project" {
  type        = string
  description = "Value of the tag 'project'"
  default     = "ai-hub-sharepoint"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the main resource group. Manually created"
  default     = "ai-hub-sharepoint"
}

variable "resources_location" {
  type        = string
  description = "Location of the resources"
  default     = "Mexico Central"

}

variable "storage_account_name" {
  type        = string
  description = "Name of the storage account. Manually created"
  default     = "endavaaihubstorage"
}

variable "storage_container" {
  type        = string
  description = "Name of the storage container. Manually created"
  default     = "ai-hub-storage-container"
}