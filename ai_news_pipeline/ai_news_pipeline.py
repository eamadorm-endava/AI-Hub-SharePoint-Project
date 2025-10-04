from loguru import logger
from ai_news_pipeline.config import AINewsSettings
from ai_news_pipeline.ai_news_pipeline_steps import retrieve_ai_news, filter_news_by_date, store_to_excel


news_settings = AINewsSettings()


def main():
    logger.info("Starting AI news retrieval process...")
    
    # Step 1: Retrieve AI news from RSS feed
    logger.info("Fetching AI news from RSS feed...")
    ai_news = retrieve_ai_news(news_settings.NEWS_URL, search_keywords=news_settings.SEARCH_KEYWORDS)
    logger.info(f"Retrieved {len(ai_news)} news articles:")

    # Step 2: Filter news articles by date (last 2 days)
    logger.info(f"Filtering news articles from the last {news_settings.DAYS_BACK} days...")
    ai_news = filter_news_by_date(df=ai_news, date_column=news_settings.DATE_COLUMN, days=news_settings.DAYS_BACK)
    logger.info(f"{len(ai_news)} articles remain after date filtering.")

    # Step 3: Store the filtered news articles to an Excel file
    logger.info("Storing AI news into an Excel file...")
    store_to_excel(ai_news, news_settings.LOCAL_FILE_PATH)
    logger.info(f"AI news successfully stored in {news_settings.LOCAL_FILE_PATH}")


if __name__ == "__main__":
    main()
