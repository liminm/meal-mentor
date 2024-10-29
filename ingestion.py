from pathlib import Path
from typing import List

import pandas as pd

import minsearch


def ingest_data(file_path: Path = Path('../data/data.csv'), text_fields: List[str] = None):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Convert text fields to strings
    if text_fields:
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].astype(str)

    # Convert the dataframe to a dictionary
    return df.to_dict(orient='records')


def get_index(
        documents,
        text_fields: List[str],
        keyword_fields: List[str],
        search_index=minsearch.Index
):
    # TODO move this check to ingest data; to more elegantly
    for doc in documents:
        for key in doc:
            if isinstance(doc[key], float):
                doc[key] = str(doc[key])
            elif isinstance(doc[key], int):
                doc[key] = str(doc[key])
            elif not isinstance(doc[key], str):
                doc[key] = str(doc[key])
            else:
                doc[key] = doc[key]


    index = search_index(
        text_fields=text_fields,
        keyword_fields=keyword_fields
    )

    index.fit(documents)

    return index


from pathlib import Path
from typing import List

import pandas as pd

import minsearch


def ingest_data(file_path: Path = Path('../data/data.csv'), text_fields: List[str] = None):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Convert text fields to strings
    if text_fields:
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].astype(str)

    # Convert the dataframe to a dictionary
    return df.to_dict(orient='records')


def get_index(
        documents,
        text_fields: List[str],
        keyword_fields: List[str],
        search_index=minsearch.Index
):
    # TODO move this check to ingest data; to more elegantly
    for doc in documents:
        for key in doc:
            if isinstance(doc[key], float):
                doc[key] = str(doc[key])
            elif isinstance(doc[key], int):
                doc[key] = str(doc[key])
            elif not isinstance(doc[key], str):
                doc[key] = str(doc[key])
            else:
                doc[key] = doc[key]


    index = search_index(
        text_fields=text_fields,
        keyword_fields=keyword_fields
    )

    index.fit(documents)

    return index
