# Terraform in Azure

## [Authenticate Terraform to Azure](https://learn.microsoft.com/en-us/azure/developer/terraform/authenticate-to-azure?tabs=bash)

First of all, you need an Azure subscription.

Terraform only supports authenticating to Azure with the Azure CLI. Authenticating using Azure Powershell isn't supported.


## Create an Azure Resource Group

1.- Create a file named providers.tf, and insert the code that is shown [here](https://learn.microsoft.com/en-us/azure/developer/terraform/create-resource-group?tabs=azure-cli#implement-the-terraform-code).

2.- Create a file called main.tf, where you will create a ***resource group***.

A **resource group** is a container that logically organizes related resources for an Azure solution. These resources can be anything from VM and storage accounts, to databases and web apps. 

Essentially, it's a way to group resources that are related to a specific application or project, making them easier to manage, deploy, update, and delete as a single unit.

Basically, its the same as a project in Google Cloud.

## Creation of an Storage Blob Container

To do so, you first need a resource_group, then, you need to create a ***storage account***.

An **Storage Account** contains all of your Azure Storage data objects: blobs, files, queues, and tables. The storage account provides an unique namespace for your Azure Storage data that's accessible from anywhere in the world over HTTP or HTTPS. Data in your storage account is durable and highly available, secure, and massively scalable.

There are different storage accounts, see this [link](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview#types-of-storage-accounts) for more info.

***The name of the storage account must be unique within Azure. No two storage accounts can have the same name.**

## Store the tf.state remotely

When working with CI/CD pipelines, you need a place to persist the tf.state. To do so, you first need to **manually create the following resources:**

1. **Resource Group:** You can use the Azure CLI:

        az group create --name resourcegroupname --location nameoflocation

2. **Storage Account:** Using the CLI:

        az storage account create \
        --name storageaccountname \
        --resource-group resourcegroupname \
        --location locationname \
        --sku Standard_LRS \
        --kind StorageV2 \
        --enable-hierarchical-namespace true

3. **Storage Container:** Using the CLI:

        az storage container create \
        --name storagecontainername \
        --account-name storageaccountname \
        --auth-mode login


After manually creating those resources, create a ***backend.tf*** file (No variables are allowed here):


    terraform {
        backend "azurerm" {
            resource_group_name  = "resourcegroupname"
            storage_account_name  = "storageaccountname"
            container_name        = "storagecontainername"
            key                   = "terraform.tfstate"
        }
    }

Then, you can normally set

        terraform init
        terraform apply

To start saving the tf.state in the storage container in Azure