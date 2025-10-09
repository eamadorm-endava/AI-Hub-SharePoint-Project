import concurrent.futures
import pandas as pd
from loguru import logger
from typing import Optional
from ai_news_pipeline.extractors.news.news_extractors import NewsExtractor


def extract_from_feed(feed_url: str) -> Optional[pd.DataFrame]:
    """
    Extracts articles from a specific feed_url
    """
    extractor = NewsExtractor()
    extractor.set_current_feed_url(feed_url)

    return extractor.get_articles()


def extract_from_multiple_feed_urls(feed_urls: list[str]) -> Optional[pd.DataFrame]:
    """
    Extract the articles from different feed urls using parallelization

    Args:
        feed_urls: list[str] -> List of feed_urls

    Returns:
        all_articles: Optional[pd.DataFrame] -> DataFrame containing all the articles
                                            from all the different feed urls
    """
    if not isinstance(feed_urls, list):
        logger.error("feed_urls must be a list of feed urls")
        return
    if not all(isinstance(url, str) and url != "" for url in feed_urls):
        logger.error("All the entries of the feed_urls list must be not null strings")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {
            executor.submit(extract_from_feed, url): url for url in feed_urls
        }
        results = list()

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]

            try:
                data = future.result()
                if isinstance(data, pd.DataFrame):
                    results.append(data)

            except Exception as e:
                logger.error(f"Error extracting articles from {url}: {e}")

    if results:
        return pd.concat(results)

    logger.error("No articles were extracted from any source")


def filter_by_keywords(
    df: pd.DataFrame,
    filter_column: str,
    case_sen_search_kw: list[str],
    case_insen_search_kw: list[str],
) -> pd.DataFrame:
    """
    Filter a dataframe by keywords (either case sensitive or case insensitive) over
    a filter column

    Args:
        df: pd.DataFrame -> DataFrame containing the data to be filtered
        filter_column: str -> Name of the column to filter by
        case_sen_search_kw: Optional[list[str]] -> List of Case Sensitive Search Keywords.
        case_insen_search_kw: Optional[list[str]] -> List of (Case Insensitive Search Keywords)

    Returns:
        Optional[pd.DataFrame] -> Dataframe filtered by keywords
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("The parameter 'df' must be a pandas DataFrame")
        return
    if not isinstance(filter_column, str):
        logger.error("The parameter 'filter_column' must be a not null string")
        return
    elif filter_column not in df.columns:
        logger.error(
            "'filter_column' must be the name of a column existing in the DataFrame 'df'"
        )
        return
    if not all(
        isinstance(kw_list, list)
        for kw_list in [case_sen_search_kw, case_insen_search_kw]
    ):
        logger.error(
            "The parameters 'case_sen_search_kw' and 'case_insen_search_kw' must be lists of strings"
        )
        return
    if not all(
        isinstance(kw, str) and kw != ""
        for kw in case_sen_search_kw + case_insen_search_kw
    ):
        logger.error(
            "All the entries in the lists 'case_sen_search_kw' and 'case_insen_search_kw' must "
            "be not null strings"
        )
        return

    logger.debug("Filtering articles by the next parameters...")
    logger.debug(f"{case_sen_search_kw =}")
    logger.debug(f"{case_insen_search_kw =}")
    logger.debug(f"Filtering by column: {filter_column}")

    def matches_keyword(text: str) -> bool:
        match = any(kw in text for kw in case_sen_search_kw) | any(
            kw.lower() in text.lower() for kw in case_insen_search_kw
        )

        return match

    df_copy = df.copy()

    df_copy = df_copy[df_copy[filter_column].apply(matches_keyword)]

    # Reset dataframe index to keep sequential order
    df_copy = df_copy.reset_index(drop=True)

    logger.info(
        f"Keyword filtering complete. {len(df_copy)} articles matched the criteria."
    )

    return df_copy


def filter_by_date_threshold(
    df: pd.DataFrame, filter_column: str, max_days_old: int
) -> pd.DataFrame:
    """
    Filters the articles by age since its publication date

    Args:
        max_days_old: int -> Maximum days old an article must have

    Returns:
        pd.DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("The parameter 'df' must be a pandas DataFrame")
        return
    if not isinstance(filter_column, str):
        logger.error("The parameter 'filter_column' must be a not null string")
        return
    elif filter_column not in df.columns:
        logger.error(
            "'filter_column' must be the name of a column existing in the DataFrame 'df'"
        )
        return
    if not isinstance(max_days_old, int):
        logger.error("The parameter 'max_days_old' must be a positive integer")
    elif max_days_old < 0:
        logger.error("The parameter 'max_days_old' cannot be lower than zero")
        return

    logger.info(f"Filtering articles published within the last {max_days_old} days.")

    df_copy = df.copy()

    # As publish_date is in UTC, the current_date must also be in this timezone
    current_date = pd.Timestamp.utcnow()
    max_publish_date = current_date - pd.Timedelta(days=max_days_old)

    df_copy = df_copy[df_copy[filter_column] >= max_publish_date]

    # Reset dataframe index to keep sequential order
    df_copy = df_copy.reset_index(drop=True)

    logger.info(
        f"Date filtering complete. {len(df_copy)} articles "
        "published within the allowed range."
    )

    return df_copy


def convert_datetime_columns_to_str(
    df: pd.DataFrame, string_format: str
) -> Optional[pd.DataFrame]:
    """
    Converts all the datetime columns to string columns in the final format defined

    Args:
        df: pd.DataFrame -> DataFrame containing datetime columns
        string_format: str -> String format representing the datetime value

    Returns:
        Optional[pd.DataFrame]
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("The parameter 'df' must be a pandas DataFrame.")
        return

    if not isinstance(string_format, str) or string_format.strip() == "":
        logger.error("The parameter 'string_format' must be a non-empty string.")
        return

    df_copy = df.copy()

    datetime_cols = df_copy.select_dtypes(
        include=["datetime64[ns]", "datetime64[ns, UTC]"]
    ).columns

    if not datetime_cols.any():
        logger.warning("No datetime columns found to convert.")
        return df_copy

    logger.info(f"Converting datetime columns to string format: {string_format}")
    logger.debug(f"Detected datetime columns: {list(datetime_cols)}")

    for col in datetime_cols:
        df_copy[col] = df_copy[col].dt.strftime(string_format)

    logger.info("Datetime conversion complete.")

    return df_copy
