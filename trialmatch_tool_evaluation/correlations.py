import itertools

import pandas as pd
from scipy.stats import spearmanr

from trialmatch_tool_evaluation import PLOTS_FOLDER
from trialmatch_tool_evaluation._utils import dfi_export_proxy
from trialmatch_tool_evaluation.constants import CRITERIA, K_VALUES, TrialMatchingTools
from trialmatch_tool_evaluation.metrics.ranked_metrics import (
    AP_at_k,
    NDCG_at_k,
    NFPR_at_k,
)

CORRELATIONS_FOLDER = PLOTS_FOLDER / "correlations"


def spearman_correlation(list1, list2):
    corr = spearmanr(
        [e for e in list1 if e is not None],
        [e for e in list2 if e is not None],
    )
    return round(corr.statistic, 3), corr.pvalue


def append_correlations_dict(
    correlations_dict, tool, metric1_name, metric2_name, corr, pvalue
):
    correlations_dict["tool"].append(tool)
    correlations_dict["metric_1"].append(metric1_name)
    correlations_dict["metric_2"].append(metric2_name)
    correlations_dict["correlation"].append(corr)
    correlations_dict["pvalue"].append(pvalue)


def add_correlation(df_metrics, metric1, metric2, criterium, tool, correlations):
    metric_mask = (df_metrics["criterium"] == criterium) & (df_metrics["tool"] == tool)
    metric_1_mask = (df_metrics["metric_name"] == metric1) & metric_mask
    metric_2_mask = (df_metrics["metric_name"] == metric2) & metric_mask

    metric1_values = df_metrics[metric_1_mask]["value"].dropna().tolist()
    metric2_values = df_metrics[metric_2_mask]["value"].dropna().tolist()
    corr, pvalue = spearman_correlation(metric1_values, metric2_values)

    append_correlations_dict(correlations, tool, metric1, metric2, corr, pvalue)


def main(df_metrics: pd.DataFrame):
    CORRELATIONS_FOLDER.mkdir(exist_ok=True)

    df_metrics = df_metrics.copy()
    # ----------------------------- Correlations between AP and NDCG -----------------------------

    for criterium in CRITERIA:

        correlations = {
            "tool": [],
            "metric_1": [],
            "metric_2": [],
            "correlation": [],
            "pvalue": [],
        }

        for tool in TrialMatchingTools.all():

            for k in K_VALUES:

                add_correlation(
                    df_metrics,
                    metric1=AP_at_k(k=k).name,
                    metric2=NDCG_at_k(k=k).name,
                    criterium=criterium,
                    tool=tool,
                    correlations=correlations,
                )

        df_correlations = pd.DataFrame(correlations)
        file_path = CORRELATIONS_FOLDER / f"correlations_ap_ndcg_{criterium}.png"
        dfi_export_proxy(
            df_correlations.round({"correlation": 3, "pvalue": 20}), file_path
        )

    # ----------------------- NDCG and AP correlations between ranks 3, 5, 10 -----------------------

    for criterium in CRITERIA:

        correlations = {
            "tool": [],
            "metric_1": [],
            "metric_2": [],
            "correlation": [],
            "pvalue": [],
        }

        for tool in TrialMatchingTools.all():

            for metric in [AP_at_k, NDCG_at_k, NFPR_at_k]:

                k_combinations = itertools.combinations(K_VALUES, 2)
                for k in k_combinations:

                    metric1_name = metric(k=k[0]).name
                    metric2_name = metric(k=k[1]).name

                    add_correlation(
                        df_metrics,
                        metric1_name,
                        metric2_name,
                        criterium=criterium,
                        tool=tool,
                        correlations=correlations,
                    )

        df_correlations = pd.DataFrame(correlations)
        file_path = CORRELATIONS_FOLDER / f"correlations_rank_{criterium}.png"
        dfi_export_proxy(
            df_correlations.round({"correlation": 3, "pvalue": 20}), file_path
        )


if __name__ == "__main__":
    main()
