from datetime import datetime
import re


def format_string_date(date_str: str) -> str:
    """
    Formats different types of date strings to the most common format 'YYYY-mm-dd'

    Args:
        date_str: str -> Date string with the format 'October 23, 2025', or 'Oct 23, 2025'

    Returns:
        str -> Date string in the format: '2025-10-23'
    """
    if not isinstance(date_str, str):
        raise ValueError("The date is not a string data type")

    for fmt in (r"%B %d, %Y", r"%b %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime(r"%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(f"Unrecognized date format: '{date_str}'")


def get_initial_and_final_dates(raw_date: str) -> tuple[str]:
    """
    Extracts the initial and final event's date from formats such as:
            - 'October 23 to 27, 2025'
            - 'Oct 23 to 27, 2025'
            - 'October 23 to November 1, 2025'

    In case there's a single-day event, it needs to have the format 'October 23, 2025' or 'Oct 23, 2025'

    Args:
        raw_date: str -> Date with the formats provided early

    Returns:
        tuple[str] -> Tuple of strings initial and final dates in the format '%Y-%m-%d'
    """
    year_match = re.search(r"\b\d{4}\b", raw_date)
    year = year_match.group(0) if year_match else ""

    if " to " in raw_date:
        dates = raw_date.split(" to ")  # spaces are necessary due to "October"

    elif "-" in raw_date:  # In case it does not have "to" as a date separator
        dates = raw_date.split("-")  # In case there's dates like "Oct 12-20, 2024"

    # In case there's only a single-day event
    elif re.search(r"[A-Za-z]+ \d+, \d{4}", raw_date):
        initial_date = format_string_date(raw_date)
        final_date = initial_date
        return initial_date, final_date

    else:
        raise ValueError(f"Unknown date format: {raw_date}")

    initial_date = f"{dates[0].strip()}, {year}"

    date_pattern = r"[A-Za-z]+\s\d+, \d{4}"  # Looks for 'March 12, 2025' formats

    # If no month is defined in the final_date, the month of the initial_date is set
    final_date = (
        dates[1].strip()
        if re.search(date_pattern, dates[1].strip())
        else f"{initial_date.split()[0]} {dates[1].strip()}"
    )

    # Format string dates
    initial_date = format_string_date(initial_date)
    final_date = format_string_date(final_date)

    return initial_date, final_date
