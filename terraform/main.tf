
# agent_identity is an admin entity that allows Azure resources (e.g. VM, Azure Function, etc) to automatically 
# authenticate agains other Azure services without the need of credentials of secrets
resource "azurerm_user_assigned_identity" "agent_identity" {
  name                = "agent-identity"
  location            = var.resources_location
  resource_group_name = var.resource_group_name

  tags = {
    Tower   = var.tag_tower
    Owner   = var.tag_owner
    project = var.tag_project
  }
}

resource "azurerm_key_vault" "main-key-vault" {
  name                       = "ai-hub-key-vault-endava"
  location                   = var.resources_location
  resource_group_name        = var.resource_group_name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = true

  tags = {
    Tower   = var.tag_tower
    Owner   = var.tag_owner
    project = var.tag_project
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azurerm_user_assigned_identity.agent_identity.principal_id

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete"
    ]
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete"
    ]
  }

}
################################################################### App Registration ######################################################################
# Microsoft Entra ID (Azure AD) Application registration for the AI Hub application

# Main module to create an app registration in MS Entra ID (Azure AD)
resource "azuread_application" "ai-hub-app" {
  display_name = "ai-hub-app-ms-entra"
  description  = "App registration for the AI Hub application to access SharePoint Online"
  owners       = [data.azurerm_client_config.current.object_id]

  required_resource_access {

    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph

    resource_access {
      id   = "9492366f-7969-46a4-8d15-ed1a20078fff" # Sites.ReadWrite.All
      type = "Role"
    }
  }
}

# Creation of the service principal for the app registration. 
# This is required to assign roles to the app registration
resource "azuread_service_principal" "ai-hub-sp" {
  client_id = azuread_application.ai-hub-app.client_id
  owners    = [data.azurerm_client_config.current.object_id]
}