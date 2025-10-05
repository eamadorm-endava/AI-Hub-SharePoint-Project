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
    
    n_news_extracted = len(ai_news)
    logger.info(f"{n_news_extracted} articles remain after date filtering.")

    if n_news_extracted > 0:

        # Step 3: Store the filtered news articles to an Excel file
        logger.info(f"Storing {n_news_extracted} news into an Excel file...")
        store_to_excel(ai_news, news_settings.LOCAL_FILE_PATH)
        logger.info(f"AI news successfully stored in {news_settings.LOCAL_FILE_PATH}")

    else:
        logger.info("There's no news to save into an excel file")

if __name__ == "__main__":
    main()
