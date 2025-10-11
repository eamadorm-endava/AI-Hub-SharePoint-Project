GCP_PROJECT_ID="learned-stone-454021-c8"
GCP_SA="dev-service-account@learned-stone-454021-c8.iam.gserviceaccount.com"
GCP_REGION="northamerica-south1"
ARTIFACT_REGISTRY_NAME="ai-hub-sharepoint"
NEWS_EXTRACTION_PIPELINE_IMAGE_NAME="$(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(ARTIFACT_REGISTRY_NAME)/news_extraction_pipeline:latest"

gcloud-auth:
	gcloud config unset auth/impersonate_service_account 
	gcloud auth application-default login --impersonate-service-account $(GCP_SA)
	
uv-sync:
	uv sync --all-groups

install-git-hooks: 
	uv run pre-commit install
	uv run pre-commit install-hooks

run-local-news-extraction-pipeline-endpoint:
	uv run uvicorn news_extraction_pipeline.app.main:app --reload

build-news-extraction-pipeline-image:
	docker build \
	-f news_extraction_pipeline/news_extraction_pipeline.dockerfile \
	-t $(NEWS_EXTRACTION_PIPELINE_IMAGE_NAME) \
	.

push-news-extraction-pipeline-image:
	docker push  $(NEWS_EXTRACTION_PIPELINE_IMAGE_NAME)

run-news-extraction-image:
	docker run -p 8000:8000 $(NEWS_EXTRACTION_PIPELINE_IMAGE_NAME)