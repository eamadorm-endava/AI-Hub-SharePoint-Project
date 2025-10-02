terraform {
  backend "azurerm" {
    resource_group_name  = "ai-hub-sharepoint"
    storage_account_name = "endavaaihubstorage"
    container_name       = "ai-hub-storage-container"
    key                  = "terraform.tfstate"
  }
}