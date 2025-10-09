from loguru import logger
import argparse

from ai_news_pipeline.config import AINewsConfig
from ai_news_pipeline.ai_news_pipeline_steps import (
    extract_from_multiple_feed_urls,
    filter_by_date_threshold,
    filter_by_keywords,
)
from utils.io_utils import store_df_to_excel


news_config = AINewsConfig()


def main(
    case_sen_search_kw: list[str],
    case_insen_search_kw: list[str],
    max_days_old: int,
    local_file_path: str,
    excel_sheet_name: str,
    excel_table_name: str,
):
    """
    Pipeline that extracts AI-related news from an specific website, clean, filter, and transform the data, and then
    stores them into an excel file.

    Args:
        case_sen_search_kw: list[str] -> List of case sensitive keywords to filter the AI-news by,
        case_insen_search_kw: list[str] -> List of case insensitive keywords to filter the AI-news by,
        max_days_old: int -> Number of days that you want to retrieve the data from
                            (e.g. 2 -> Get the news from the last 2 days),
        local_file_path: str -> Local path where the excel file generated will be stored
                            (e.g. -> local-file-path/file_name.xlsx)
        sheet_name: str -> Name of the Excel Sheet name where the data will be stored
        table_name: str -> Name of the Excel table where the data will be stored
    """
    logger.info("Starting AI news retrieval process...")

    # Step 1: Retrieve all the feed_urls registered in AINewsConfig class
    news_config_dict = news_config.model_dump()
    news_sources = [
        val for key, val in news_config_dict.items() if key.endswith("_FEED_URL")
    ]

    # Step 2: Get all the articles available from the different sources found
    all_articles = extract_from_multiple_feed_urls(news_sources)

    # Step 3: Filter news articles by date (last 2 days)
    logger.info(f"Filtering news articles from the last {max_days_old} days...")
    articles_filtered_by_date = filter_by_date_threshold(
        df=all_articles,
        filter_column=news_config.DATE_COLUMN,
        max_days_old=max_days_old,
    )

    # Step 4: Filter news articles by search keywords
    articles_filtered_by_keywords = filter_by_keywords(
        df=articles_filtered_by_date,
        case_insen_search_kw=case_insen_search_kw,
        case_sen_search_kw=case_sen_search_kw,
        filter_column=news_config.COLUMN_TO_FILTER_BY_KW,
    )

    # Step 5: Store the filtered news articles to an Excel file
    n_articles_extracted = len(articles_filtered_by_date)

    if n_articles_extracted > 0:
        logger.info(f"Storing {n_articles_extracted} news into an Excel file...")
        store_df_to_excel(
            df=articles_filtered_by_keywords,
            local_file_path=local_file_path,
            sheet_name=excel_sheet_name,
            table_name=excel_table_name,
        )
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
        "--max-days-old",
        type=int,
        default=news_config.MAX_DAYS_OLD,
        help="Maximum number of days to look back when retrieving news articles."
        "For example, 2 means only articles published in the last 2 days will be included.",
    )
    parser.add_argument(
        "--local-file-path",
        type=str,
        default=news_config.FILE_PATH,
        help="Path where the excel file will be stored",
    )
    parser.add_argument(
        "--excel-sheet-name",
        type=str,
        default=news_config.EXCEL_SHEET_NAME,
        help="Name of the Excel sheet where the data will be stored",
    )
    parser.add_argument(
        "--excel-table-name",
        type=str,
        default=news_config.EXCEL_TABLE_NAME,
        help="Name of the Excel table where the data will be stored",
    )

    args = parser.parse_args()

    main(
        case_sen_search_kw=args.case_sen_search_kw,  # '-' become '_'
        case_insen_search_kw=args.case_insen_search_kw,
        max_days_old=args.max_days_old,
        local_file_path=args.local_file_path,
        excel_sheet_name=args.excel_sheet_name,
        excel_table_name=args.excel_table_name,
    )
