from typing import List

import pandas as pd

from trialmatch_tool_evaluation import (
    AGGREGATION_METRICS_PATH,
    FORMATTED_CSV_PATH,
    METRICS_PATH,
    PLOTS_FOLDER,
)
from trialmatch_tool_evaluation._utils import (
    append_metrics_dict,
    dfi_export_proxy,
    intersect_binary,
    union_binary,
)
from trialmatch_tool_evaluation.constants import (
    CORPUS_CARDINALITY,
    CRITERIA,
    K_VALUES,
    STRATEGY,
    TrialMatchingTools,
)
from trialmatch_tool_evaluation.metrics import (
    FN,
    FP,
    TN,
    TP,
    Accuracy,
    AP_at_k,
    ErrorRate,
    NDCG_at_k,
    NFPR_at_k,
    Precision,
    Sensitivity,
    Specificity,
)
from trialmatch_tool_evaluation.metrics.base_metrics import Metric, RankedMetric
from trialmatch_tool_evaluation.preprocess_files import get_formatted_data


def calculate_total_specific_relevance(df_relevance, criterium, patient_id):
    total_relevance = intersect_binary(
        df_relevance[df_relevance["patient_id"] == patient_id]["eligibility"].iloc[0],
        df_relevance[df_relevance["patient_id"] == patient_id]["status"].iloc[0],
    )
    if criterium == "eligibility_and_status":
        specific_relevance = union_binary(
            df_relevance[df_relevance["patient_id"] == patient_id]["eligibility"].iloc[
                0
            ],
            df_relevance[df_relevance["patient_id"] == patient_id]["status"].iloc[0],
        )
    else:
        specific_relevance = df_relevance[df_relevance["patient_id"] == patient_id][
            criterium
        ].iloc[0]

    return total_relevance, specific_relevance


def main(formatted_data: pd.DataFrame):

    # -------------------------------------- Compute aggregation metrics --------------------------------------

    # Initialize metrics dictionary
    metrics = {
        "metric_name": [],
        "criterium": [],
        "tool": [],
        "patient_id": [],
        "value": [],
    }

    unranked_metrics: List[Metric] = [
        TP(),
        FP(),
        TN(corpus_cardinality=CORPUS_CARDINALITY),
        FN(),
        Precision(strategy=STRATEGY),
        Sensitivity(strategy=STRATEGY),
        Specificity(corpus_cardinality=CORPUS_CARDINALITY),
        Accuracy(),
        ErrorRate(strategy=STRATEGY),
    ]
    ranked_metrics: List[RankedMetric] = [
        metric
        for k in K_VALUES
        for metric in [
            AP_at_k(k=k, strategy=STRATEGY),
            NDCG_at_k(k=k, strategy=STRATEGY),
            NFPR_at_k(k=k, strategy=STRATEGY),
        ]
    ]
    trials_retrieved_count_by_patient = {
        patient_id: len(nct_ids)
        for patient_id, nct_ids in zip(
            formatted_data["patient_id"], formatted_data["nct_id"]
        )
    }

    for criterium in CRITERIA:
        for tool in TrialMatchingTools.all():
            for _, patient_row in formatted_data.iterrows():
                ranking = patient_row[tool]
                relevance = patient_row[criterium]
                patient_id = patient_row["patient_id"]

                total_relevance, specific_relevance = (
                    calculate_total_specific_relevance(
                        formatted_data, criterium, patient_id
                    )
                )

                for metric in unranked_metrics + ranked_metrics:
                    current_score = metric.compute(
                        ranking=ranking,
                        relevance=relevance,
                        nb_all_trials_retrieved=trials_retrieved_count_by_patient[
                            patient_id
                        ],
                        total_relevance=total_relevance,
                        specific_relevance=specific_relevance,
                    )

                    append_metrics_dict(
                        metrics_dict=metrics,
                        metric=metric,
                        score=current_score,
                        tool=tool,
                        patient_id=patient_id,
                        criterium=criterium,
                    )

    # -------------------------------------- Save metrics --------------------------------------

    df_metrics = pd.DataFrame(metrics)
    df_aggregation_metrics = pd.concat(
        [
            df_metrics.groupby(["metric_name", "criterium", "tool"])["value"]
            .agg(["mean", "median", "std", "count"])
            .reset_index(),
            df_metrics.groupby(["metric_name", "criterium"])["value"]
            .agg(["mean", "median", "std", "count"])
            .reset_index(),
        ]
    ).fillna({"tool": "all"})

    print("Number of metrics : ", len(df_aggregation_metrics))

    df_metrics.to_csv(METRICS_PATH, index=False)
    df_aggregation_metrics.to_csv(AGGREGATION_METRICS_PATH, index=False)

    metrics_for_png = [
        TP.name,
        Precision.name,
        Accuracy.name,
        Sensitivity.name,
        Specificity.name,
        AP_at_k.generic_name,
        NDCG_at_k.generic_name,
        NFPR_at_k.generic_name,
        ErrorRate.name,
    ]

    # Save metrics as png
    for metric in metrics_for_png:
        sub_metrics = df_aggregation_metrics[
            df_aggregation_metrics["metric_name"].str.contains(metric.format(k=""))
        ][
            ["metric_name", "criterium", "tool", "count", "mean", "median", "std"]
        ].reset_index(
            drop=True
        )

        file_path = PLOTS_FOLDER / f"{metric}_results_strategy_{STRATEGY}.png"
        dfi_export_proxy(sub_metrics.round(5), file_path)

    return df_metrics, df_aggregation_metrics


if __name__ == "__main__":
    formatted_data = get_formatted_data(FORMATTED_CSV_PATH)
    main(formatted_data)
