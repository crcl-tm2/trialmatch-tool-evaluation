import pandas as pd
import plotly.express as px

from trialmatch_tool_evaluation import PLOTS_FOLDER
from trialmatch_tool_evaluation.metrics import FN, FP, TN, TP


def plot_difference_from_median(df, df_median):

    criterium = df["criterium"].iloc[0]
    metric = df["metric_name"].iloc[0]
    tool = df["tool"].iloc[0]

    df["median_over_tools"] = df["patient_id"].apply(
        lambda x: df_median[df_median["patient_id"] == x]["median"].iloc[0]
    )
    df = df.assign(diff_from_median=df["value"] - df["median_over_tools"])
    df = df.dropna()
    df["patient_id"] = df["patient_id"].apply(lambda x: str(x))

    fig = px.bar(
        df,
        x="patient_id",
        y="diff_from_median",
        title=f"{metric} difference from median for {tool} on criterium {criterium} ({len(df)} patients)",
        width=800,
        opacity=1,
    )
    fig.update_traces(width=0.7)
    fig.update_xaxes(showticklabels=False, title_text="Patients")
    fig.update_yaxes(title_text="Difference from median")

    img_path = (
        PLOTS_FOLDER
        / "diff_from_median"
        / f"{metric}_diff_from_median_{criterium}_{tool}.png"
    )
    fig.write_image(img_path)


def plot_confusion_matrix(data, criterium, tool):
    fig = px.imshow(
        data,
        x=["Retrieved", "Not retrieved"],
        y=["Relevant", "Not relevant"],
        text_auto=True,
        title=f"Confusion matrix for {tool} on {criterium} criterium",
    )
    fig.update_xaxes(side="top")

    img_path = (
        PLOTS_FOLDER / "confusion_matrices" / f"confusion_matrix_{criterium}_{tool}.png"
    )
    fig.write_image(img_path)


def init_folders():
    (PLOTS_FOLDER / "confusion_matrices").mkdir(exist_ok=True)
    (PLOTS_FOLDER / "diff_from_median").mkdir(exist_ok=True)


def main(df_metrics: pd.DataFrame, df_aggregation_metrics: pd.DataFrame):
    init_folders()

    # --------------------------------- Plot difference from median ---------------------------------

    df_median_over_tools = (
        df_metrics[df_metrics["tool"] != "all"]
        .groupby(["metric_name", "criterium", "patient_id"])["value"]
        .agg(["median"])
        .reset_index()
    )

    for group_name, group_values in df_metrics.groupby(
        ["criterium", "metric_name", "tool"]
    ):
        criterium = group_name[0]
        metric = group_name[1]
        subset_median_over_tools = df_median_over_tools[
            (df_median_over_tools["criterium"] == criterium)
            & (df_median_over_tools["metric_name"] == metric)
        ]
        plot_difference_from_median(group_values, subset_median_over_tools)

    # ----------------------------------- PLot confusion matrices -----------------------------------

    print("\nlog : \n", df_aggregation_metrics)

    for group_name, group_values in df_aggregation_metrics.groupby(
        ["criterium", "tool"]
    ):
        tp = group_values[group_values["metric_name"] == TP.name]["mean"].iloc[0]
        fn = group_values[group_values["metric_name"] == FN.name]["mean"].iloc[0]
        fp = group_values[group_values["metric_name"] == FP.name]["mean"].iloc[0]
        tn = group_values[group_values["metric_name"] == TN.name]["mean"].iloc[0]

        criterium = group_name[0]
        tool = group_name[1]

        plot_confusion_matrix(
            [[round(tp, 2), round(fn, 2)], [round(fp, 2), round(tn, 2)]],
            criterium,
            tool,
        )


if __name__ == "__main__":
    main()
