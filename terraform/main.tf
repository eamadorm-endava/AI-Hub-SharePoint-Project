
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
}
