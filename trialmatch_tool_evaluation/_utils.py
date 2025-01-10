import dataframe_image as dfi
import pandas as pd

from trialmatch_tool_evaluation import (
    AGGREGATION_METRICS_PATH,
    CLB_CLINICAL_TRIALS_PATH,
    METRICS_PATH,
)
from trialmatch_tool_evaluation.metrics.base_metrics import Metric


def get_clb_clinical_trials_file():
    return pd.read_csv(CLB_CLINICAL_TRIALS_PATH, sep=";")


def get_metrics():
    return pd.read_csv(METRICS_PATH)


def get_aggregation_metrics():
    return pd.read_csv(AGGREGATION_METRICS_PATH)


def append_metrics_dict(
    metrics_dict, metric: Metric, score, criterium=None, tool=None, patient_id=None
):
    metrics_dict["metric_name"].append(metric.name)
    metrics_dict["value"].append(score)
    metrics_dict["patient_id"].append(patient_id)

    if tool:
        metrics_dict["tool"].append(tool)
    if criterium:
        metrics_dict["criterium"].append(criterium)


def dfi_export_proxy(obj, filename):
    dfi.export(
        obj=obj,
        filename=filename,
        table_conversion="matplotlib",
    )


def union_binary(list1, list2):
    return [max(list1[i], list2[i]) for i in range(len(list1))]


def intersect_binary(list1, list2):
    return [min(list1[i], list2[i]) for i in range(len(list1))]
