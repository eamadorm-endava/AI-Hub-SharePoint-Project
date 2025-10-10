# Pulls a Python image suited for this project
FROM python:3.12-slim

ENV UV_VERSION=0.8.9

# Copy pyproject.toml and uv.lock in the working directory
COPY pyproject.toml uv.lock ./

# Upgrade pip and install the required uv version
RUN pip install --upgrade pip &&\
    pip install uv==${UV_VERSION}

# Create a requirements.txt from the pyproject.toml
RUN uv export --group "dev" --group "ai-news-automation" --no-hashes -o requirements.txt

RUN pip install --no-cache-dir -r requirements.txt 

# Creation of the main directory where everything will be stored
WORKDIR /news_extraction_pipeline

# Copying all the necessary files
COPY news_extraction_pipeline/. .

# Expose the port where the api will listen
EXPOSE 8000

WORKDIR /.

# Execute the API
CMD ["uvicorn", "news_extraction_pipeline.app.main:app", "--host", "0.0.0.0", "--port", "8000"]