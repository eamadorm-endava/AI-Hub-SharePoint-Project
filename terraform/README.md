# Terraform in GCP

## [Authenticate Terraform to GCP](https://cloud.google.com/docs/terraform/authentication)

First, you need a GCP Project. Terraform can authenticate to GCP in a few ways, but the most common is trough Application Default Credentials (ADC), which is a strategy used by the authentication libraries to automatically find credentials based on the application environment.

When using ADC, Terraform can run in either a development or production environment without changing how it authenticates to Google Cloud services and APIs.

### Authenticate using a user account

In the terminal, make sure you have the gcloud CLI, and run:

        gcloud auth application-default login

this will create ADCs with your user account, if you want to impersonate a service account, use:

        gcloud auth application-default login --impersonate-service-account <your-service-account-email>


**When using Terraform with GCP services such as Compute Engine, App Engine, and CloudRun functions, you can attach a user-managed service account to resources**

## Create a [main.tf](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started) file

In this file, include the following configuration:

        provider "google" {
                project = "<your-project-id>"
                region  = "<where-resources-will-be-created>"
                zone    = "<where-resources-will-be-created>"
        }

Then, you can normally start adding resources in this file

## Store the terraform.tfstate remotely

For teamwork or CI/CD pipelines, you need to store the terraform.tfstate file remotely so its state can be shared and persisted. In GCP, you use a GCS bucket for this.

You only need to manually create one resource: the GCS bucket to hold the state file.

1. Create the GCS Bucket using the CLI (gsutil): You must create this bucket before running Terraform.

        gcloud storage create bucket <bucket-name> --location <location>

2. Create a backend.tf file (No variables are allowed in this file) with the following data:

        terraform {
                backend "gcs" {
                        bucket = "<name-of-bucket-manually-created>"
                        prefix = "terraform/state"
                }
        }

3. Now, you can initialize Terraform and apply your configuration. Terraform will automatically detect the backend configuration and store the state file in your GCS bucket.

        terraform init
        terraform apply
