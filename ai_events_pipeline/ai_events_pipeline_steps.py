import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas.tseries.offsets import MonthBegin
from loguru import logger

from ai_events_pipeline.events_auxiliars import get_initial_and_final_dates


def retrieve_ai_events(events_url: str) -> list[dict]:
    """
    Fetches AI event data from a webpage and returns it as a list of dictionaries, each dictionary is an event.

    Args:
        events_url (str): URL of the page containing the event table.

    Returns:
        list[dict[str, str]]: Extracted events with Title, Dates, Location, and Link.
    """
    # Step 1: Fetch the page
    headers = {
        "User-Agent": "Mozilla/5.0"
    }  # To avoid get uncomplete data from the website

    logger.info("Sending request to fetch web data")
    response = requests.get(events_url, headers=headers)

    if response.status_code != 200:
        raise ValueError(
            f"The request to {events_url} failed. Status code: {response.status_code}, {response.text}"
        )

    logger.info("Extracting AI events...")
    soup = BeautifulSoup(response.content, "html.parser")

    # Step 2: Search for the tbody element, which contains the table needed
    tbody = soup.find("tbody", class_="row-striping")
    rows = tbody.find_all("tr")

    # Step 3: Extract the data from the table
    conferences = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            dates = cols[0].get_text(strip=True)
            title_tag = cols[1].find("a")
            title = (
                title_tag.get_text(strip=True)
                if title_tag
                else cols[1].get_text(strip=True)
            )
            link = (
                title_tag["href"].strip()
                if title_tag and "href" in title_tag.attrs
                else None
            )
            location = cols[2].get_text(strip=True)

            conferences.append(
                {"Title": title, "Dates": dates, "Location": location, "Link": link}
            )

    if conferences:
        logger.info("Retrieval succeeded")
        return conferences

    else:
        logger.info("Retrieval failed. No data was fetched")


def filter_upcoming_events_by_month(
    conferences: list[dict[str]], months_in_future: int
) -> pd.DataFrame:
    """
    Filters a list of conference events to include only those occurring within a specified number of future months.

    This function expects each event dictionary to contain the keys: "Title", "Dates", "Location", and "Link".
    It parses the "Dates" field to extract initial and final dates, filters events based on whether their final
    date falls within the current month and the specified number of months ahead, and returns a cleaned DataFrame
    with formatted date strings suitable for Excel export.

    Args:
        conferences (list[dict[str]]): A list of dictionaries representing event metadata.
        months_in_future (int): Number of months ahead to include events (e.g. 3 → events within the next 3 months).

    Returns:
        pd.DataFrame: A DataFrame containing filtered events with formatted initial and final dates.
    """
    mandatory_dict_keys = ["Title", "Dates", "Location", "Link"]

    if not isinstance(conferences, list):
        raise TypeError("conferences parameter must be a list of dictionaries")

    test_event_dict = conferences[0]

    if not all(
        [dict_key in mandatory_dict_keys for dict_key in test_event_dict.keys()]
    ):
        raise AttributeError(
            "Dictionaries from 'conferences' must have the following keys: \n"
            f"{'\n'.join(mandatory_dict_keys)}"
        )

    ai_events = pd.DataFrame(conferences)

    # Get initial and final dates from the events
    ai_events[["initial_date", "final_date"]] = (
        ai_events["Dates"].apply(get_initial_and_final_dates).apply(pd.Series)
    )

    # Converting initial_date and final_date to datetime data types
    ai_events.initial_date = pd.to_datetime(ai_events.initial_date)
    ai_events.final_date = pd.to_datetime(ai_events.final_date)

    # Delete unnecessary columns
    ai_events = ai_events.drop("Dates", axis=1)

    # Get today's date
    today = pd.Timestamp.today()

    # Get the first day of the current month
    first_day_current_month = today.replace(day=1)

    # Get the first day of the month, three months from now
    first_day_plus_n_months = first_day_current_month + MonthBegin(months_in_future + 1)

    # Filter for events where final_date is lower than the first day of the current month plus 3 months
    next_events = ai_events[
        (ai_events.final_date < first_day_plus_n_months)
        & (ai_events.final_date >= first_day_current_month)
    ]

    # Returning the datetime columns to string format to avoid issues when exporting to Excel
    next_events.initial_date = next_events["initial_date"].dt.strftime(
        r"%Y-%m-%dT08:00:00Z"
    )
    next_events.final_date = next_events["final_date"].dt.strftime(
        r"%Y-%m-%dT18:00:00Z"
    )

    return next_events
