import requests
from bs4 import BeautifulSoup
from datetime import datetime


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
    return [
        container.find("img").get("src")
        for container in containers_with_images
        if container.find("img").get("width") == "800"
    ][0]
