import pandas as pd
import plotly.express as px

from trialmatch_tool_evaluation import FORMATTED_CSV_PATH, PLOTS_FOLDER
from trialmatch_tool_evaluation._utils import union_binary
from trialmatch_tool_evaluation.constants import (
    CRITERIA,
    DISPLAYED_CRITERIA,
    PLOT_COLORS,
    TUMOR_TYPES_TRANSLATION,
    UNIQUE_CRITERIA_CATEGORIES,
    TrialMatchingTools,
)
from trialmatch_tool_evaluation.metrics import FP
from trialmatch_tool_evaluation.patient_data import PatientData
from trialmatch_tool_evaluation.preprocess_files import get_formatted_data


def plot_error_rates(df_errors):
    total_per_tool = df_errors.groupby("tool")["nb_errors"].agg("sum")
    percentages = [
        df_errors.loc[i, "nb_errors"]
        / total_per_tool.loc[df_errors.loc[i, "tool"]]
        * 100
        for i in range(len(df_errors))
    ]
    df_errors = df_errors.assign(percent=percentages)
    df_errors["criterium"] = df_errors["criterium"].apply(
        lambda x: DISPLAYED_CRITERIA[x]
    )

    fig = px.bar(
        df_errors,
        x="tool",
        y="nb_errors",
        color="criterium",
        text=df_errors.apply(
            lambda x: "{0:1.2f} ({1:1.1f}%)".format(x["nb_errors"], x["percent"]),
            axis=1,
        ),
        title="Cause of false positive errors (eligibility, status, or both) for each tool",
        category_orders={
            "criterium": ["Eligibility", "Eligibility and status", "Status"]
        },
        color_discrete_sequence=PLOT_COLORS,
    )
    fig.update_xaxes(title_text="Tool")
    fig.update_yaxes(title_text="Average number of false positives per patient")
    fig.update_layout(
        legend=dict(
            title_text="Cause of false positives",
            orientation="h",
            x=0.5,
            xanchor="center",
            y=1.1,
        ),
        uniformtext_minsize=12,
        uniformtext_mode="hide",
    )
    fig.write_image(PLOTS_FOLDER / "nb_errors_bar_plot.png")


def plot_exclusion_criteria(df, nb_patients, colors, tool="all", tumor_type="all"):

    if tumor_type == "all":
        subset = df
    else:
        subset = df[df["tumor_type"] == tumor_type]

    if tool == "all":
        all_categories = sum(
            [l for l in subset["exclusion_criteria_all_tools"].tolist()], []
        )
        x_range = [0, 301]
    else:
        all_categories = sum(
            [l for l in subset[f"exclusion_criteria_{tool}"].tolist()], []
        )
        x_range = [0, 121]
    unique_categories = list(set(all_categories))
    df = pd.DataFrame(
        {
            "category": unique_categories,
            "value": [
                len([k for k in all_categories if k == c]) for c in unique_categories
            ],
        }
    )
    df = df.assign(percent=lambda x: x["value"] / df["value"].sum() * 100)
    df = df.sort_values(by="value", ascending=False)
    tumor_type = TUMOR_TYPES_TRANSLATION[tumor_type].lower()

    fig = px.bar(
        df,
        x="value",
        y="category",
        color="category",
        text=df.apply(
            lambda x: "{0:1} ({1:1.1f}%)".format(x["value"], x["percent"]),
            axis=1,
        ),
        title=f"Criteria categories that make the patients ineligible on false positives trials \nfor {nb_patients} patients for {tool} tool for {tumor_type} tumors",
        color_discrete_map=colors,
    )
    fig.update_traces(textfont_size=10)
    fig.update_xaxes(title_text="Number of errors", range=x_range)
    fig.update_yaxes(title_text="Category of error")
    fig.update_layout(title_font_size=12, showlegend=False)
    fig.write_image(
        PLOTS_FOLDER / f"exclusion_criteria_{tool}_tool_{tumor_type}_tumors.png"
    )


def main(formatted_data: pd.DataFrame):

    # --------------------------------- Plot error rates ---------------------------------

    tools_list, criteria_list, nb_errors_list = [], [], []
    nb_patients = len(formatted_data)

    for tool in TrialMatchingTools.all():
        for criterium in CRITERIA:
            tools_list.append(tool)
            criteria_list.append(criterium)

            nb_errors = 0
            for i in formatted_data["patient_id"].tolist():
                patient_data = formatted_data[formatted_data["patient_id"] == i]
                ranking = patient_data[tool].tolist()[0]
                if criterium == "eligibility_and_status":
                    relevance = union_binary(
                        patient_data["eligibility"].iloc[0],
                        patient_data["status"].iloc[0],
                    )
                else:
                    relevance = patient_data[criterium].tolist()[0]
                nb_errors += FP().compute(ranking, relevance)
            nb_errors_list.append(nb_errors / nb_patients)

    df_errors = pd.DataFrame(
        {"tool": tools_list, "criterium": criteria_list, "nb_errors": nb_errors_list}
    )

    plot_error_rates(df_errors)

    # --------------------------- Errors on exclusion criteria ---------------------------

    exclusion_criteria_colors = {
        UNIQUE_CRITERIA_CATEGORIES[k]: PLOT_COLORS[k]
        for k in range(len(UNIQUE_CRITERIA_CATEGORIES))
    }

    data = {
        "patient_id": [],
        "tumor_type": [],
        "exclusion_criteria_all_tools": [],
        "exclusion_criteria_per_tool": {t: [] for t in TrialMatchingTools.all()},
    }

    for _, patient_values in formatted_data.iterrows():
        patient_data = PatientData.from_ranking(patient_values.to_dict())
        data["patient_id"].append(patient_data.patient_id)
        data["tumor_type"].append(patient_data.tumor_type)

        data["exclusion_criteria_all_tools"].append(
            [
                c
                for c in (
                    patient_data.exclusion_category_1
                    + patient_data.exclusion_category_2
                )
                if c is not None
            ]
        )

        for t in TrialMatchingTools.all():
            tool_criteria = []
            for i in range(patient_data.nb_all_trials_retrieved):
                if patient_data.rankings[t][i] != 0:
                    if patient_data.exclusion_category_1[i] is not None:
                        tool_criteria.append(patient_data.exclusion_category_1[i])
                    if patient_data.exclusion_category_2[i] is not None:
                        tool_criteria.append(patient_data.exclusion_category_2[i])
            data["exclusion_criteria_per_tool"][t].append(tool_criteria)

    print("Total number of patients : ", nb_patients)

    for t in TrialMatchingTools.all():
        data[f"exclusion_criteria_{t}"] = data["exclusion_criteria_per_tool"][t]
    del data["exclusion_criteria_per_tool"]
    df = pd.DataFrame(data)

    plot_exclusion_criteria(
        df, nb_patients, exclusion_criteria_colors, tool="all", tumor_type="all"
    )
    for t in TrialMatchingTools.all():
        plot_exclusion_criteria(
            df, nb_patients, exclusion_criteria_colors, tool=t, tumor_type="all"
        )

    for t in ["DIGESTIF", "MAMMAIRE", "SARCOMES", "UROLOGIE", "GYNECOLOGIQUE"]:
        plot_exclusion_criteria(
            df, nb_patients, exclusion_criteria_colors, tool="all", tumor_type=t
        )


if __name__ == "__main__":
    formatted_data = get_formatted_data(FORMATTED_CSV_PATH)
    main(formatted_data)
