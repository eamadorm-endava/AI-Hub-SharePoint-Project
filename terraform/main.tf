# Hola!, este archivo fue modificado por un AI-Agent!
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}


############## ARTIFACT REGISTRY ###############

# Make sure docker is connected to the artifact
# check this: https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling
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


# ################# Bucket to store blobs ###################
resource "google_storage_bucket" "static" {
  name     = var.main_bucket_name
  location = var.gcp_region
  #  storage_class = var.main_bucket_storage_class
  autoclass {
    enabled = var.main_bucket_autoclass_enabled
  }
  uniform_bucket_level_access = false # Enforce uniform access control, no ACLs
}


# ################# CloudRun - News Extraction Pipeline API ###################

resource "google_cloud_run_v2_service" "news_extraction_pipeline" {
  name                = var.news_extraction_pipeline_instance
  location            = var.gcp_region
  client              = "terraform"
  deletion_protection = false

  template {

    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${var.artifact_registry_name}/${var.news_extraction_pipeline_image_name}:${var.news_extraction_pipeline_image_tag}"
      ports {
        container_port = var.news_extraction_pipeline_port
      }
      resources {
        limits = {
          memory = "2Gi"
          cpu    = "1"
        }
      }
    }
    scaling {
      # Min instances
      min_instance_count = 0
      max_instance_count = 2
    }
  }
}

# Set who can call the news_extraction_pipeline API
resource "google_cloud_run_v2_service_iam_member" "news_extraction_pipeline_auth" {
  location = google_cloud_run_v2_service.news_extraction_pipeline.location
  name     = google_cloud_run_v2_service.news_extraction_pipeline.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}


########################################## BigQuery ###########################################
resource "google_bigquery_dataset" "main_dataset" {
  dataset_id  = var.dataset_id
  description = "The datasets in Bigquery can be considered as schemas in any other structured database. So this is the schema for the tables."
  location    = var.gcp_region

  labels = {
    env = "default"
  }
}

resource "google_bigquery_table" "news_metadata" {
  dataset_id = google_bigquery_dataset.main_dataset.dataset_id
  table_id   = var.news_metadata_table_id

  deletion_protection = false

  labels = {
    env         = "default"
    primary_key = "news_id"
  }

  schema = <<EOF

[
  {
    "name": "news_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "ID of the news"
  },
  {
    "name": "title",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Title of the news"
  },
  {
    "name": "published_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "Timestamp when the news was published"
  },
  {
    "name": "extracted_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "Timestamp when the news was added to the table"
  },
  {
   "name": "news_link",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Link where the news can be read"
  },
  {
    "name": "image_link",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Link to the main image of the news"
  }
]
EOF
}
