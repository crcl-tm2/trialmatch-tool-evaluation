from ast import literal_eval
from pathlib import Path

import pandas as pd


def get_formatted_data(formatted_csv_path: Path):
    rankings = pd.read_csv(formatted_csv_path)
    for column in set(rankings.columns) - {
        "patient_id",
        "genes",
        "tumor_type",
    }:
        rankings[column] = rankings[column].apply(
            lambda x: literal_eval(x) if x is not None else None
        )

    rankings.loc[rankings["genes"].isna(), "genes"] = None
    return rankings
