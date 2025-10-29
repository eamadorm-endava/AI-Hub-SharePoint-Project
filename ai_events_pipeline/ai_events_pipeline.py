from loguru import logger
import argparse

from ai_events_pipeline.config import AIEventsConfig
from ai_events_pipeline.ai_events_pipeline_steps import (
    retrieve_ai_events,
    filter_upcoming_events_by_month,
)
from utils.io_utils import store_df_to_excel


events_config = AIEventsConfig()


def main(
    ai_events_url: str,
    months_in_future: int,
    local_file_path: str,
    excel_sheet_name: str,
    excel_table_name: str,
) -> None:
    """
    Pipeline that extracts AI-related events from an specific website, transforms the data, and
    stores them into an excel file

    Args:
        ai_events_web_url: str -> URL from the website containing the AI-Events required to be obtained
        months_in_future: int -> Max months in the future the AI-Events must start in
        local_file_path: str -> Local path where the excel file generated will be stored
                            (e.g. -> local-file-path/file_name.xlsx)
        sheet_name: str -> Name of the Excel Sheet name where the data will be stored
        table_name: str -> Name of the Excel table where the data will be stored
    """

    logger.info("Starting AI Events retrieval pipeline...")

    # Step 1: Retrieve AI Events from the web
    logger.info("Fetching AI Events from the website...")
    ai_events_list = retrieve_ai_events(events_url=ai_events_url)
    logger.info(f"Retrieved {ai_events_list} events.")

    # Step 2: Filter upcoming events by month
    logger.info(f"Get the events from the next {months_in_future} months...")
    ai_events_filtered = filter_upcoming_events_by_month(
        conferences=ai_events_list, months_in_future=months_in_future
    )

    n_events_extracted = len(ai_events_filtered)
    logger.info(f"{n_events_extracted} events remain after date filtering.")

    if n_events_extracted > 0:
        # Step 3: Store the filtered events to an Excel file
        logger.info(f"Storing {n_events_extracted} news into an Excel file...")
        store_df_to_excel(
            df=ai_events_filtered,
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
        "--ai-events-url",
        type=str,
        default=events_config.TOP_AI_CONFERENCES,
        help="URL where the AI-events will be obtained from",
    )
    parser.add_argument(
        "--months-in-future",
        type=int,
        default=events_config.MONTHS_IN_FUTURE,
        help="Max months in the future the AI-Events must start in",
    )
    parser.add_argument(
        "--local-file-path",
        type=str,
        default=events_config.AI_EVENTS_FILE_PATH,
        help="Path where the excel file will be stored",
    )
    parser.add_argument(
        "--excel-sheet-name",
        type=str,
        default=events_config.EXCEL_SHEET_NAME,
        help="Name of the Excel sheet where the data will be stored",
    )
    parser.add_argument(
        "--excel-table-name",
        type=str,
        default=events_config.EXCEL_TABLE_NAME,
        help="Name of the Excel table where the data will be stored",
    )

    args = parser.parse_args()

    main(
        ai_events_url=args.ai_events_url,
        months_in_future=args.months_in_future,
        local_file_path=args.local_file_path,
        excel_sheet_name=args.excel_sheet_name,
        excel_table_name=args.excel_table_name,
    )
