import itertools

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats

from trialmatch_tool_evaluation import PLOTS_FOLDER, RESULTS_FOLDER
from trialmatch_tool_evaluation._utils import dfi_export_proxy
from trialmatch_tool_evaluation.constants import TrialMatchingTools

TTEST_PATH = RESULTS_FOLDER / f"t_test_results.csv"
TTEST_FOLDER = PLOTS_FOLDER / f"t_tests"
BOXPLOT_PATH = PLOTS_FOLDER / "boxplots"


def run_t_test(tool_a_scores, tool_b_scores):
    if len(tool_a_scores) != len(tool_b_scores):
        raise Exception()
    t_test_result = stats.ttest_rel(tool_a_scores, tool_b_scores)
    t_test_confidence_interval = t_test_result.confidence_interval()
    difference_of_means = np.mean(tool_a_scores) - np.mean(tool_b_scores)

    return {
        "p_value": t_test_result.pvalue,
        "inf": t_test_confidence_interval.low,
        "mean": difference_of_means,
        "sup": t_test_confidence_interval.high,
    }


def get_ttests():
    return pd.read_csv(TTEST_PATH)


def main(df_metrics: pd.DataFrame):
    BOXPLOT_PATH.mkdir(exist_ok=True)
    TTEST_FOLDER.mkdir(exist_ok=True)

    df_without_error_rate = df_metrics[df_metrics["metric_name"] != "ErrorRate"]

    sns.set_theme(rc={"figure.figsize": (5, 5)})

    tool_combinations = list(itertools.combinations(TrialMatchingTools.all(), 2))
    ttest_results = []

    for group_name, group_values in df_without_error_rate.groupby(
        ["metric_name", "criterium"]
    ):
        metric = group_name[0]
        criterium = group_name[1]

        tool_values = {}
        for tool, values in group_values.groupby("tool"):
            tool_values[tool] = values.dropna(subset="value").reset_index(drop=True)

        current_group_df = group_values.dropna(subset="value").reset_index(drop=True)
        ax = plt.axes()
        sns.boxplot(
            data=current_group_df,
            y="value",
            x="tool",
            hue="tool",
        ).set(title=f"{metric} on {criterium}", xlabel="tool", ylabel=f"{metric}")

        y_min = ax.get_ylim()[0]
        y_max = ax.get_ylim()[1]

        ax.set(ylim=(y_min, y_max * 1.5))

        for tool_a, tool_b in tool_combinations:
            tool_a_scores = tool_values[tool_a]["value"].tolist()
            tool_b_scores = tool_values[tool_b]["value"].tolist()

            test_results = run_t_test(tool_a_scores, tool_b_scores)

            current_comparison_name = f"{tool_a}_VS_{tool_b}"
            ttest_results.append(
                {
                    "metric": metric,
                    "criterium": criterium,
                    "tool_1": tool_a,
                    "tool_2": tool_b,
                }
                | test_results
            )

            ax.annotate(
                text=get_bracket_name(test_results["p_value"]),
                xy=brackets_dict[current_comparison_name]["xy"],
                xytext=brackets_dict[current_comparison_name]["xytext"],
                xycoords="axes fraction",
                ha="center",
                va="bottom",
                arrowprops=dict(
                    arrowstyle=f'-[, widthB={brackets_dict[current_comparison_name]["widthB"]}, lengthB=1.0',
                    lw=1.0,
                    color="k",
                ),
            )

        plt.savefig(BOXPLOT_PATH / f"{metric}-{criterium}.png")
        plt.close()

    # Save results as csv
    df_t_tests = pd.DataFrame(ttest_results)
    df_t_tests.to_csv(TTEST_PATH, index=False)

    for metric, ttest_by_metric in df_t_tests.groupby("metric"):
        dfi_export_proxy(
            ttest_by_metric.round({"inf": 3, "mean": 3, "sup": 3, "p_value": 5}),
            TTEST_FOLDER / f"t_test_results_for_{metric}.png",
        )


def get_bracket_name(pvalue):
    if pvalue > 0.05:
        return "NS"
    if pvalue < 0.0001:
        return "+++"
    return "+"


brackets_dict = {
    f"{TrialMatchingTools.DigitalECMT}_VS_{TrialMatchingTools.Klineo}": {
        "xy": (0.25, 0.8),
        "xytext": (0.25, 0.81),
        "widthB": 2.8,
    },
    f"{TrialMatchingTools.DigitalECMT}_VS_{TrialMatchingTools.Trialing}": {
        "xy": (0.375, 0.71),
        "xytext": (0.375, 0.72),
        "widthB": 5.7,
    },
    f"{TrialMatchingTools.DigitalECMT}_VS_{TrialMatchingTools.ScreenAct}": {
        "xy": (0.5, 0.92),
        "xytext": (0.5, 0.93),
        "widthB": 8.6,
    },
    f"{TrialMatchingTools.Klineo}_VS_{TrialMatchingTools.Trialing}": {
        "xy": (0.5, 0.8),
        "xytext": (0.5, 0.81),
        "widthB": 2.8,
    },
    f"{TrialMatchingTools.Klineo}_VS_{TrialMatchingTools.ScreenAct}": {
        "xy": (0.625, 0.86),
        "xytext": (0.625, 0.87),
        "widthB": 5.7,
    },
    f"{TrialMatchingTools.Trialing}_VS_{TrialMatchingTools.ScreenAct}": {
        "xy": (0.75, 0.8),
        "xytext": (0.75, 0.81),
        "widthB": 2.8,
    },
}

if __name__ == "__main__":
    main()
