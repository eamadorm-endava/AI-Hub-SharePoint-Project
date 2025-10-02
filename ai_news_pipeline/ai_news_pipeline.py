import feedparser
from loguru import logger
from ai_news_pipeline.config import AINewsSettings
from ai_news_pipeline.news_auxiliars import format_date, extract_news_image


news_settings = AINewsSettings()


def retrieve_ai_news(url: str) -> list[dict]:
    """
    Retrieve AI news from the given RSS feed URL.

    Args:
        url (str): URL of the RSS feed.

    Returns:
        list[dict]: List of dictionaries containing news details.
    """
    if not isinstance(url, str):
        raise ValueError("Input must be a string representing the RSS feed URL.")
    feed = feedparser.parse(url)

    # Extract relevant data from feed entries
    ai_news = [
        {
            "title": entry.title,
            "news_link": entry.link,
            "publish_date": format_date(entry.published),
            "image_link": extract_news_image(entry.link),
            "summary": entry.summary,
        }
        for entry in feed.entries
    ]

    return ai_news


def main():
    logger.info("Starting AI news retrieval process...")

    logger.info("Fetching AI news from RSS feed...")
    ai_news = retrieve_ai_news(news_settings.NEWS_URL)
    logger.info(f"Retrieved {len(ai_news)} news articles:")
    logger.info(
        f"News Titles: \n{'\n'.join([article.get('title') for article in ai_news])}"
    )


if __name__ == "__main__":
    main()
