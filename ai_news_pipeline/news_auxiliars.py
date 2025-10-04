import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
import os


def format_date(date_str: str) -> str:
    """
    Format a RFC 2822 date string to ISO 8601 format with 'Z' suffix.

    Args:
        date_str (str): Date string in RFC 2822 format (e.g., 'Fri 09 Oct 2020 14:19:00 +0000').

    Returns:
        str: Date string in ISO 8601 format (e.g., '2020-10-09 14:19:00Z').
    """
    if not isinstance(date_str, str):
        raise ValueError(
            "Input must be a string in the format '%a, %d %b %Y %H:%M:%S %z' (e.g.: 'Fri 09 Oct 2020 14:19:00 +0000')."
        )

    date_time = datetime.strptime(date_str, r"%a, %d %b %Y %H:%M:%S %z")

    return date_time.strftime(r"%Y-%m-%d %H:%M:%SZ")


def extract_news_image(news_url: str) -> str:
    """
    Extract the main image URL from a news article page.

    Args:
        news_url (str): URL of the news article.

    Returns:
        str: URL of the main image in the article.
    """
    if not isinstance(news_url, str):
        raise ValueError("Input must be a string representing the news article URL.")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(news_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")

    soup = BeautifulSoup(response.content, "html.parser")

    all_containers = soup.select(".elementor-widget-container")

    containers_with_images = [c for c in all_containers if c.find("img")]
    image = [
        container.find("img").get("src")
        for container in containers_with_images
        if container.find("img").get("width") == "800"
    ][0]

    return image


def store_to_excel(ai_news: list[dict[str, str]], local_file_path: str) -> None:
    """
    Store AI news data into an Excel file.

    Args:
        ai_news (list[dict[str, str]]): List of dictionaries containing news details.
        local_file_path (str): Path to the output Excel file. (e.g., '')
    
    Returns:
        None
    """
    if not isinstance(ai_news, list) or not all(isinstance(item, dict) for item in ai_news):
        raise ValueError("Input must be a list of dictionaries representing AI news data.")
    if not isinstance(local_file_path, str): 
        raise ValueError("File path must be a string representing a valid local file path.")

    local_path = '/'.join(local_file_path.split("/")[:-1])

    if not os.path.exists(local_path):
        raise ValueError(f"The directory {local_path} does not exist.")
    elif not local_file_path.endswith('.xlsx'):
        raise ValueError("The file name must end with '.xlsx'.")

    ai_news_df = pd.DataFrame(ai_news)

    with pd.ExcelWriter(local_file_path, engine='openpyxl') as writer:
        ai_news_df.to_excel(writer, index=False, sheet_name='AI-News')
        workbook  = writer.book
        worksheet = writer.sheets["AI-News"]
        (max_row, max_col) = ai_news_df.shape

        # Calculate the table range in Excel format (e.g., "A1:D10")
        table_ref = f"A1:{get_column_letter(max_col)}{max_row + 1}"

        table = Table(displayName="AIEventsTable", ref=table_ref)
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                            showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        table.tableStyleInfo = style
        worksheet.add_table(table)

