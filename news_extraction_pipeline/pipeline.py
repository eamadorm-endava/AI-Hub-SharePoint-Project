import pandas as pd
from loguru import logger
from typing import Optional

from news_extraction_pipeline.config import AINewsConfig
from news_extraction_pipeline.schemas import PipelineArgs
from news_extraction_pipeline.pipeline_steps import (
    extract_from_multiple_feed_urls,
    filter_by_date_threshold,
    filter_by_keywords,
    convert_datetime_columns_to_str,
)

news_config = AINewsConfig()


def main(
    case_sen_search_kw: Optional[list[str]] = None,
    case_insen_search_kw: Optional[list[str]] = None,
    max_days_old: Optional[int] = None,
) -> pd.DataFrame:
    """
    Pipeline that extracts AI-related news from an specific website, clean, filter, and transform the data, and then
    stores them into an excel file.

    Args:
        case_sen_search_kw: Optional[list[str]] -> List of case sensitive keywords to filter the AI-news by,
        case_insen_search_kw: Optional[list[str]] -> List of case insensitive keywords to filter the AI-news by,
        max_days_old: Optional[int] -> Number of days that you want to retrieve the data from

    Returns:
        pd.DataFrame -> pandas DataFrame containing AI-related news
    """
    logger.info("Starting AI news retrieval process...")

    raw_args = {
        "case_sen_search_kw": case_sen_search_kw,
        "case_insen_search_kw": case_insen_search_kw,
        "max_days_old": max_days_old,
    }

    filtered_args = {k: v for k, v in raw_args.items() if v is not None}
    pipe_args = PipelineArgs(**filtered_args)

    # Step 1: Retrieve all the feed_urls registered in AINewsConfig class
    news_config_dict = news_config.model_dump()
    news_sources = [
        val for key, val in news_config_dict.items() if key.endswith("_FEED_URL")
    ]

    # Step 2: Get all the articles available from the different sources found
    all_articles = extract_from_multiple_feed_urls(news_sources)

    # Step 3: Filter news articles by date (last 2 days)
    logger.info(
        f"Filtering news articles from the last {pipe_args.max_days_old} days..."
    )
    articles_filtered_by_date = filter_by_date_threshold(
        df=all_articles,
        filter_column=news_config.DATE_COLUMN,
        max_days_old=pipe_args.max_days_old,
    )

    # Step 4: Filter news articles by search keywords
    articles_filtered_by_keywords = filter_by_keywords(
        df=articles_filtered_by_date,
        case_insen_search_kw=pipe_args.case_insen_search_kw,
        case_sen_search_kw=pipe_args.case_sen_search_kw,
        filter_column=news_config.COLUMN_TO_FILTER_BY_KW,
    )

    # Step 5: Convert datetime columns to strings, if any
    final_articles = convert_datetime_columns_to_str(
        articles_filtered_by_keywords, string_format=news_config.DATE_STRING_FORMAT
    )

    return final_articles
