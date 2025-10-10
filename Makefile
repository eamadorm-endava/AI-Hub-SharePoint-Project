GCP_PROJECT_ID=""
GCP_SA=""
GCP_REGION="northamerica-south1"
ARTIFACT_REGISTRY_NAME=""
NEWS_EXTRACTION_PIPELINE_IMAGE_NAME="$(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(ARTIFACT_REGISTRY_NAME)/news_extraction_pipeline:latest"

run-local-news-extraction-pipeline-endpoint:
	uv run uvicorn news_extraction_pipeline.app.main:app --reload

build-news-extraction-pipeline-image:
	docker build \
	-f news_extraction_pipeline/news_extraction_pipeline.dockerfile \
	-t $(NEWS_EXTRACTION_PIPELINE_IMAGE_NAME) \
	.

run-news-extraction-image:
	docker run -p 8000:8000 $(NEWS_EXTRACTION_PIPELINE_IMAGE_NAME)