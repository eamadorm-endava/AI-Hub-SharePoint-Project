GCP_PROJECT_ID=p-dev-gce-60pf
GCP_SA=ai-hub-sharepoint-sa@p-dev-gce-60pf.iam.gserviceaccount.com
GCP_TERRAFORM_SA=terraform-ai-hub-sharepoint@p-dev-gce-60pf.iam.gserviceaccount.com
GCP_REGION=northamerica-south1
ARTIFACT_REGISTRY_NAME=ai-hub-sharepoint
NEWS_EXTRACTION_PIPELINE_IMAGE_NAME="$(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(ARTIFACT_REGISTRY_NAME)/news_extraction_pipeline:latest"

gcloud-auth:
	gcloud config unset auth/impersonate_service_account 
	gcloud auth application-default login --impersonate-service-account $(GCP_SA)
	export GOOGLE_APPLICATION_CREDENTIALS=${HOME}/.config/gcloud/application_default_credentials.json

gcloud-auth-terraform:
	gcloud config unset auth/impersonate_service_account 
	gcloud auth application-default login --impersonate-service-account $(GCP_TERRAFORM_SA)
	export GOOGLE_APPLICATION_CREDENTIALS=${HOME}/.config/gcloud/application_default_credentials.json

uv-sync:
	uv sync --all-groups

install-git-hooks: 
	uv run pre-commit install
	uv run pre-commit install-hooks

run-agent:
	uv run python -m agent.agent

run-local-news-extraction-pipeline-endpoint:
	uv run uvicorn news_extraction_pipeline.app.main:app --reload

build-news-extraction-pipeline-image:
	docker build \
	-f news_extraction_pipeline/news_extraction_pipeline.dockerfile \
	-t $(NEWS_EXTRACTION_PIPELINE_IMAGE_NAME) \
	.

link-docker-to-artifact-registry:
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev

push-news-extraction-pipeline-image:
	docker push  $(NEWS_EXTRACTION_PIPELINE_IMAGE_NAME)

run-news-extraction-image:
	docker run -p 8000:8000 $(NEWS_EXTRACTION_PIPELINE_IMAGE_NAME)