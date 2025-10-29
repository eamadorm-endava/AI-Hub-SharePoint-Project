# Pulls a Python image suited for this project
FROM python:3.12-slim

ENV UV_VERSION=0.8.9

# Creation of the main directory where everything will be stored
WORKDIR /pipeline

# Copy pyproject.toml and uv.lock in the working directory
COPY pyproject.toml uv.lock ./

# Upgrade pip and install the required uv version
RUN pip install --upgrade pip &&\
    pip install uv==${UV_VERSION}

# Create a requirements.txt from the pyproject.toml
RUN uv export --group "dev" --group "ai-news-automation" --group "gcp" --no-hashes -o requirements.txt

RUN pip install --no-cache-dir -r requirements.txt 

# Copying all the necessary files
COPY database/. ./database/
COPY news_extraction_pipeline/. ./news_extraction_pipeline/
COPY utils/. ./utils/
COPY agent/config.py agent/__init__.py ./agent/

# Expose the port where the api will listen
EXPOSE 8000


# Execute the API
CMD ["uvicorn", "news_extraction_pipeline.app.main:app", "--host", "0.0.0.0", "--port", "8000"]