# AI-Hub-SharePoint-Project

The purpose of this project to automate some of the most repetitive tasks that the [AI-Hub SharePoint](https://endava.sharepoint.com/sites/AINewsletter) needs, such as publishing articles, news, and events.

Currently working on three main automations:

- [*news_extraction_pipeline/*](news_extraction_pipeline/) -   Development copleted, working on its deployment

- [*events_extraction_pipeline/*](ai_events_pipeline/) - Status: Stand by until *news_extraction_pipeline/* is deployed - progress: 60 %

- [*agent/*](agent/) - Status: Awaiting for approval

## Repository Structure

- *agent/*: Folder containing all the code related to the AI-agent
- *events_extraction_pipeline/*: Extraction and publication of AI-related events 
- *news_extraction_pipeline/*: Extraction and publication of AI-related news
- *notebooks/*: To test some code before creating Python scripts
- *terraform/*: All the cloud infrastructure required

## How to Run this Repository

### 1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) (python dependency-manager)

### 2. Install [terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) (Infrastructure as Code)

### 3. Install the [Azure CLI](https://learn.microsoft.com/es-es/cli/azure/install-azure-cli?view=azure-cli-latest)


### 4. Install all the Python dependencies

In a terminal at the root of this repository, execute

        uv sync

***Completing this point will allow you to run all the notebooks and Python scripts**

### 5. Login to your Azure account

In a terminal at the root of this repository, execute

        az login

### 6. Activate pre-commit (Optional)

You can use pre-commit to format and lint-check Python and Terraform files before each commit using Ruff and Terraform FMT

In a terminal at the root of this repository, execute

        uv run pre-commit install

