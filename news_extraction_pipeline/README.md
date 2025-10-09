## AI-News Extraction Pipeline

This module is the first stage of the complete AI-News Pipeline.

The full pipeline was originally implemented in PowerAutomate using an RSS connector, which retrieves structured data from RSS feeds, which typically contain:

- Title

- Publish date

- Link to news

- Link to image


To generate these RSS feeds (referred to as ***feed_urls*** in this project) from standard website URLs, an external platform was previously used. However, due to cost considerations, it is now necessary to replace that dependency.

This module serves as a replacement for the external platform, enabling direct extraction of the required information from website URLs without relying on third-party RSS generators.

## Full AI-News Pipeline -> (Currently active in PowerAutomate)

1. **Extract AI-related news** from different sources ([MIT](https://web.mit.edu/) and [AI News](https://www.artificialintelligence-news.com/)) using a RSS connector

2. **Clean and preprocess the extracted data**: 

    - Format dates and titles to ensure compatibility with SharePoint.

    - Filter articles based on keywords in their titles (e.g. *AI, ChatGPT, Gemini, LLM*)
    - Filter articles by publish date, retaining only those published within a period of time (defined in 2 days for this project, as the pipeline is daily executed)
    
3. **Deduplication and store:**

    - Checks whether each article already exists in the target SharePoint list.

    - If it’s new, store it; otherwise, discard it to avoid duplication.

## New Pipeline Proposed

The primary limitation preventing full implementation of this pipeline in PowerAutomate is its inability to execute Python scripts.

Additionally, the permissions required to connect Python directly to SharePoint via Microsoft Graph are too elevated, making approval difficult.

However, PowerAutomate can make HTTP requests to external APIs and connect to Azure Blob Storage. Based on this, the proposed pipeline is as follows:

| Pipeline Step| Executor |
|:--|:--:|
| 1. Trigger an Azure Function via HTTP request | PowerAutomate |
| 2. Extract data from RSS URLs | AzureFunction (Python) |
| 3. Clean and preprocess the extracted data | AzureFunction (Python) |
| 4. Store the processed RSS data in Azure Blob Storage | AzureFunction (Python)|
| 5. Retrieve data from Azure Blob Storage | PowerAutomate |
| 6. Check if the data already exists in the SharePoint list | PowerAutomate |
| 7. If not present, save it to the SharePoint list | PowerAutomate |

Finally, PowerApps uses this SharePoint list data to create a visual component embedded within the SharePoint page.

****This pipeline is scheduled to run once per day.**

## Module Responsabilities

This module handles:

- **Extraction**

    Retrieves raw RSS data from website URLs.

- **Cleansing**

    Format dates and titles to ensure smooth integration with PowerAutomate. 
    
- **Preprocessing**

    Filters articles by publish date and keywords to retain only AI-related content.

## Module Structure

The pipeline is designed with modularity and extensibility in mind, allowing each component to handle a specific stage of the extraction process. Below is an overview of the core modules and their roles:

### [extractors/](/news_extraction_pipeline/extractors/)

Contains the logic for extracting data from RSS feeds and image URLs from news articles.

### [selectors/](/news_extraction_pipeline/selectors/)

Contains the bridge logic for dynamically selecting the appropriate extractor class.
