import feedparser
from datetime import datetime, timezone, timedelta
import pandas as pd
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
from loguru import logger
import os

from ai_news_pipeline.news_auxiliars import format_date, extract_news_image


def retrieve_ai_news(url: str, search_keywords: list[str]) -> pd.DataFrame:
    """
    Retrieve AI-related news from the given RSS feed URL.

    Args:
        url (str): URL of the RSS feed.
        search_keywords (list[str]): List of keywords to filter AI news articles.

    Returns:
        pd.DataFrame: List of dictionaries containing news details.
    """
    if not isinstance(url, str):
        raise ValueError("Input must be a string representing the RSS feed URL.")
    if not isinstance(search_keywords, list) or not all(isinstance(keyword, str) for keyword in search_keywords):
        raise ValueError("Keywords must be a list of strings.")

    logger.info("Fetching RSS feed...")
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        raise RuntimeError(f"Error parsing RSS feed: {e}")

    
    # Extract relevant data from feed entries  
    logger.info(f"Filtering news articles based on keywords: {search_keywords}")
    ai_news = [
        {
            "title": entry.title.replace('\'', ''), # Remove single quotes to avoid issues in SharePoint
            "news_link": entry.link,
            "image_link": extract_news_image(entry.link), # Extract main image from the news article
            "publish_date": format_date(entry.published)
        }
        for entry in feed.entries if any(keyword.lower() in entry.title.lower() for keyword in search_keywords)
        ]
    
    ai_news_df = pd.DataFrame(ai_news)

    return ai_news_df


def filter_news_by_date(df: pd.DataFrame, date_column: str = "publish_date", days: int = 2) -> pd.DataFrame:
    """
    Filter news articles in the DataFrame that are newer than a specified number of days.

    Args:
        df (pd.DataFrame): DataFrame containing news articles.
        date_column (str): Name of the column containing publication dates. Date format must be '%Y-%m-%d %H:%M:%SZ'.
        days (int): Number of days to filter by. Example: 2, for articles newer than the last 2 days.

    Returns:
        pd.DataFrame: Filtered DataFrame with articles newer than the specified number of days.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")
    if date_column not in df.columns:
        raise ValueError(f"Column '{date_column}' does not exist in the DataFrame.")
    if not isinstance(days, int) or days < 0:
        raise ValueError("Days must be a non-negative integer.")

    mexico_city_timezone = timezone(timedelta(hours=-6))
    now_utc = datetime.now(timezone.utc)
    mexico_city_time = now_utc.astimezone(mexico_city_timezone)

    # To keep the original DataFrame unchanged
    df_copy = df.copy()

    # Ensure the date column is a datetime type
    df_copy[date_column] = pd.to_datetime(df_copy[date_column], format=r'%Y-%m-%d %H:%M:%SZ', utc=True)

    filtered_df = df_copy[df_copy[date_column] >= mexico_city_time - timedelta(days=days)]
    
    # Convert the date column back to string format
    filtered_df.loc[:, f"{date_column}_str"] = filtered_df[date_column].dt.strftime(r'%Y-%m-%d %H:%M:%SZ')

    filtered_df.drop(date_column, axis=1, inplace=True)

    filtered_df.rename(columns = {f"{date_column}_str": date_column}, inplace=True)
    
    return filtered_df


def store_to_excel(ai_news: pd.DataFrame, local_file_path: str) -> None:
    """
    Store AI news data into an Excel file.

    Args:
        ai_news (pd.DataFrame): DataFraem containing AI news data.
        local_file_path (str): Path to the output Excel file. (e.g., '')
    
    Returns:
        None
    """
    if not isinstance(ai_news, pd.DataFrame):
        raise ValueError("ai_news must be a pandas DataFrane containing AI news data.")
    if not isinstance(local_file_path, str): 
        raise ValueError("File path must be a string representing a valid local file path.")

    local_path = '/'.join(local_file_path.split("/")[:-1])

    if not os.path.exists(local_path):
        raise ValueError(f"The directory {local_path} does not exist.")
    elif not local_file_path.endswith('.xlsx'):
        raise ValueError("The file name must end with '.xlsx'.")


    with pd.ExcelWriter(local_file_path, engine='openpyxl') as writer:
        ai_news.to_excel(writer, index=False, sheet_name='AI-News')
        worksheet = writer.sheets["AI-News"]
        (max_row, max_col) = ai_news.shape

        # Calculate the table range in Excel format (e.g., "A1:D10")
        table_ref = f"A1:{get_column_letter(max_col)}{max_row + 1}"

        table = Table(displayName="RecentAINews", ref=table_ref)
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                            showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        table.tableStyleInfo = style
        worksheet.add_table(table)
