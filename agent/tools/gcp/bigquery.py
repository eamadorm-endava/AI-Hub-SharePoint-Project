from loguru import logger
from utils.gcp.bigquery import query_data
from database.tables.bigquery import NewsExtractionTable
from database.schemas import NewsMetadata


bq_table = NewsExtractionTable()


def query_news_table() -> list[NewsMetadata]:
    """
    Extract the content of the BigQuery table "news extraction"

    Returns:
        list[NewsMetadata] -> List of NewsMetadata objects, each object represents a table row
    """
    logger.info("Retrieving data from BigQuery...")

    query = f"""
            select
              title, 
              published_at,
              extracted_at,
              news_link 
            from `{bq_table.project_id}.{bq_table.dataset_id}.{bq_table.name}`
            """
    try:
        row_iterator = query_data(query)

    except Exception as e:
        logger.error(f"An error occurred while querying the table: {e}")
        return

    results = [
        NewsMetadata(
            title=row.title,
            published_at=row.published_at,  # Already a datetime object
            extracted_at=row.extracted_at,
            news_link=row.news_link,
        )
        for row in row_iterator
    ]

    logger.info(f"{len(results)} rows extracted")

    return results
