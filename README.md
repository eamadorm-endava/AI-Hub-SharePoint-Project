# AI-Hub-SharePoint-Agent

This repository contains the code that generates an AI agent capable to create SharePoint pages related to AI topics inside the AI-Hub

## Proposed Architecture

The architecture proposed, considering SharePoint is a Microsoft Service, is describe as:

| Component  | Function |
|:--:|:--:|
|Azure OpenAI / Azure AI Services | Process instructions and generate a desing |
| Azure Functions / Logic Apps | Orchestrate the page creation (Python) |
| Microsoft Graph API | Create and publish the page in SharePoint |
| Azure Key Vault | Protect secrets and tokens |
| Power Automate (optional) | Trigger workflow from event |


The AI Agent should work as follows:

1. **User sends an instruction**: "Create a page related to AI Agents"

2. **Azure OpenAI generates a desing** (JSON with sections, titles, images, etc)

3. **Azure Function takes the desing and calls Microsoft Graph API** to create the SharePoint page

4. **The page is automatically published in SharePoint**

## Repository Structure

- *agent/*: Generation logic using Azure OpenAI
- *azure/function/*: Function that receives the desing and publish it into SharePoint
- *graph/*: Microsoft Graph API
- *docs/*: Technical documentation
- *.github/workflows/*: CI/CD pipelines

