# Extractor Selectors Module

The ImageExtractorSelector class is responsible for dynamically selecting the appropriate image extractor based on the base URL of a news article. It acts as a bridge between the feed URL and the correct scraping logic, ensuring that each article is enriched with its corresponding image link.

This module is a key component of the AI-News Pipeline, enabling scalable and maintainable image extraction across multiple news sources.

Different news websites have different HTML structures, requiring custom scraping logic to extract the main image. Instead of hardcoding logic for each source, this module provides a centralized selector that:

Maps each known base URL to its corresponding ImageExtractor class.

Automatically chooses the correct extractor based on the feed URL.

Keeps the system extensible — new extractors can be added with minimal changes.

## Problems Solved

- **Hardcoded Logic:** 

    Avoids manually selecting extractors for each feed URL.

- **Scalability Issues:** 

    Supports easy addition of new extractors without modifying core pipeline logic.

- **Inconsistent Matching:** 

    Uses regex to reliably extract base URLs and match them to registered extractors.

- **Silent Failures:** 

    Logs warnings when no extractor is found, helping trace missing configurations.

## How it works

Check this [notebook](/notebooks/image_extractor_selectors.ipynb) to see its implementation