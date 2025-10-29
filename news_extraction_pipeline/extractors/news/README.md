# News Extractor Module

The NewsExtractor class is designed to retrieve structured AI-related news from RSS feeds and enrich it with image links extracted directly from the article pages. This module is part of the broader AI-News Pipeline and serves as the core engine for transforming raw RSS data into a clean, enriched dataset ready for integration with SharePoint.

The Python library feedparser is used to extract data from RSS feeds, but it only retrieves the following fields:

- title

- news link
- publish date

However, the AI-SharePoint visual also requires an image link to represent each news item.

To address this, the NewsExtractor integrates with the ImageExtractorSelector module, which dynamically selects the appropriate image scraper for each news source. This allows the pipeline to enrich RSS data with the main image from the article page.

## Problems Solved

- **Limited RSS Data:** 

    RSS feeds lack image links, which are essential for visual representation in SharePoint.

- **Dynamic Source Handling:** 
    
    Different news sources require different scraping strategies. This module automatically selects the correct image extractor based on the feed URL.

- **Redundant Extraction Avoidance:** 
    
    The module tracks previously extracted feed URLs to avoid unnecessary reprocessing.

- **Timezone Normalization:** 
    
    Publish dates are standardized to UTC to ensure consistency across sources.

## Design Highlights

### ImageExtractorSelector Integration

When a new feed URL is set, the module automatically selects the appropriate image extractor using the ImageExtractorSelector. This ensures that each article is enriched with its corresponding image link.

### Smart Feed Management

The module tracks the current and previous feed URLs. If the same feed is requested again, it returns cached results instead of reprocessing.

### Clean Data Output

The final output is a pandas.DataFrame containing:

- Title
- News link
- Image Link
- Publish Date (converted to UTC)

### How it works

Check this [notebook](/notebooks/news_extractors.ipynb) to see its implementation