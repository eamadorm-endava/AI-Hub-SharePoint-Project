from fastapi import FastAPI
from news_extraction_pipeline.app.models import ExtractionPipelineResponse
from news_extraction_pipeline.schemas import PipelineArgs
from news_extraction_pipeline.pipeline import main
import pandas as pd

app = FastAPI()


@app.post("/extract_articles", response_model=ExtractionPipelineResponse)
def get_articles(pipeline_args: PipelineArgs):
    articles_extracted = main(
        case_sen_search_kw=pipeline_args.case_sen_search_kw,
        case_insen_search_kw=pipeline_args.case_insen_search_kw,
        max_days_old=pipeline_args.max_days_old,
    )

    if not isinstance(articles_extracted, pd.DataFrame):  # if not DataFrame, is None
        articles_extracted = list()

    else:
        # Create a list of dictionaries - expectede by ExtractionPipelineResponse
        articles_extracted = articles_extracted.to_dict(orient="records")

    response = ExtractionPipelineResponse(
        total_articles=len(articles_extracted), data=articles_extracted
    )

    return response
