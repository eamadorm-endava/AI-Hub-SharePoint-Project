from loguru import logger
import argparse

from ai_news_pipeline.config import AINewsConfig
from ai_news_pipeline.ai_news_pipeline_steps import (
    retrieve_ai_news,
    filter_news_by_date,
    store_to_excel,
)


news_config = AINewsConfig()


def main(
    case_sen_search_kw: list[str],
    case_insen_search_kw: list[str],
    days_back: int,
    local_file_path: str,
):
    """
    Pipeline that extracts AI-related news from an specific website, clean, filter, and transform the data, and then
    stores them into an excel file.

    Args:
        case_sen_search_kw: list[str] -> List of case sensitive keywords to filter the AI-news by,
        case_insen_search_kw: list[str] -> List of case insensitive keywords to filter the AI-news by,
        days_back: int -> Number of days that you want to retrieve the data from
                            (e.g. 2 -> Get the news from the last 2 days),
        local_file_path: str -> Local path where the excel file generated will be stored
                            (e.g. -> local-file-path/file_name.xlsx)
    """
    logger.info("Starting AI news retrieval process...")

    # Step 1: Retrieve AI news from RSS feed
    logger.info("Fetching AI news from RSS feed...")
    ai_news = retrieve_ai_news(
        url=news_config.NEWS_URL,
        case_sen_search_kw=case_sen_search_kw,
        case_insen_search_kw=case_insen_search_kw,
    )
    logger.info(f"Retrieved {len(ai_news)} news articles:")

    # Step 2: Filter news articles by date (last 2 days)
    logger.info(f"Filtering news articles from the last {days_back} days...")
    ai_news = filter_news_by_date(
        df=ai_news, date_column=news_config.DATE_COLUMN, days=days_back
    )

    n_news_extracted = len(ai_news)
    logger.info(f"{n_news_extracted} articles remain after date filtering.")

    if n_news_extracted > 0:
        # Step 3: Store the filtered news articles to an Excel file
        logger.info(f"Storing {n_news_extracted} news into an Excel file...")
        store_to_excel(ai_news, local_file_path)
        logger.info(f"AI news successfully stored in {local_file_path}")

    else:
        logger.info("There's no news to save into an excel file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI-Hub SharePoint: Pipeline to extract AI News from the web"
    )

    parser.add_argument(
        "--case-insen-search-kw",
        type=lambda keywords_string: [
            keyword for keyword in keywords_string.split(",")
        ],
        default=news_config.CASE_INSEN_SEARCH_KW,
        help="Keywords to filter the news from (expected input: 'AI,Machine Learning,NLP')",
    )
    parser.add_argument(
        "--case-sen-search-kw",
        type=lambda keywords_string: [
            keyword for keyword in keywords_string.split(",")
        ],
        default=news_config.CASE_SEN_SEARCH_KW,
        help="Keywords to filter the news from (expected input: 'AI,Machine Learning,NLP')",
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=news_config.DAYS_BACK,
        help="Number of days in the past to back and retrieve the news from. example: 2 -> Get the news from the last 2 days",
    )
    parser.add_argument(
        "--local-file-path",
        type=str,
        default=news_config.LOCAL_FILE_PATH,
        help="Path where the excel file will be stored",
    )

    args = parser.parse_args()

    main(
        case_sen_search_kw=args.case_sen_search_kw,  # '-' become '_'
        case_insen_search_kw=args.case_insen_search_kw,
        days_back=args.days_back,
        local_file_path=args.local_file_path,
    )
