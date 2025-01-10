from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go

from trialmatch_tool_evaluation import FORMATTED_CSV_PATH, PLOTS_FOLDER
from trialmatch_tool_evaluation._utils import (
    append_metrics_dict,
    dfi_export_proxy,
    get_clb_clinical_trials_file,
)
from trialmatch_tool_evaluation.constants import (
    CRITERIA,
    PLOT_COLORS,
    TrialMatchingTools,
)
from trialmatch_tool_evaluation.metrics import (
    NbTrials,
    NbTrialsWhenNotZero,
    PercentageOutOfCLBTrials,
)
from trialmatch_tool_evaluation.preprocess_files import get_formatted_data


def plot_nb_trials_hist(df_nb_trials):

    fig = go.Figure()
    for i, tool in enumerate(TrialMatchingTools.all()):
        values = df_nb_trials[df_nb_trials["tool"] == tool]["value"].tolist()
        fig.add_trace(
            go.Histogram(
                x=values,
                name=tool,
                xbins=dict(end=10, size=1),
                texttemplate="%{y}",
                marker_color=PLOT_COLORS[i],
                opacity=0.75,
            )
        )
    fig.update_layout(
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.05, yanchor="middle"),
        width=1200,
        title_text="Number of proposed trials per patient for each tool",
        xaxis_title_text="Number of trials",
        yaxis_title_text="Number of patients",
        bargap=0.15,
        bargroupgap=0.05,
    )
    fig.write_image(PLOTS_FOLDER / "nb_trials_histogram.png")


def preprocess_clb_clinical_trials(criterium="eligibility_and_status"):
    df_clb_clinical_trials = get_clb_clinical_trials_file()
    if criterium != "eligibility":
        df_clb_clinical_trials = df_clb_clinical_trials[
            df_clb_clinical_trials["STATUT_RECRUTEMENT"] == "Ouverte aux inclusions"
        ]
    df_clb_clinical_trials = df_clb_clinical_trials[
        df_clb_clinical_trials["VALEUR"].str.contains("NCT")
    ]
    clb_open_nct_ids = df_clb_clinical_trials["VALEUR"].unique()
    return clb_open_nct_ids


@dataclass
class PatientTrialAnnotationCount:
    noteligibile_on_criteria: int
    eligibile_on_criteria: int
    noteligibile_on_status: int
    eligibile_on_status: int

    @staticmethod
    def from_df(formatted_data: pd.DataFrame):
        return PatientTrialAnnotationCount(
            eligibile_on_criteria=sum(sum(ct) for ct in formatted_data["eligibility"]),
            noteligibile_on_criteria=sum(
                1
                for relevants in formatted_data["eligibility"]
                for relevance in relevants
                if relevance == 0
            ),
            eligibile_on_status=sum(sum(ct) for ct in formatted_data["status"]),
            noteligibile_on_status=sum(
                1
                for relevants in formatted_data["status"]
                for relevance in relevants
                if relevance == 0
            ),
        )

    @property
    def noteligibile_on_criteria_proportion(self):
        return 100 * self.noteligibile_on_criteria / self.criteria_total

    @property
    def eligibile_on_criteria_proportion(self):
        return 100 * self.eligibile_on_criteria / self.criteria_total

    @property
    def noteligibile_on_status_proportion(self):
        return 100 * self.noteligibile_on_status / self.status_total

    @property
    def eligibile_on_status_proportion(self):
        return 100 * self.eligibile_on_status / self.status_total

    @property
    def total(self):
        return (
            self.noteligibile_on_criteria
            + self.eligibile_on_criteria
            + self.noteligibile_on_status
            + self.eligibile_on_status
        )

    @property
    def eligible_total(self):
        return self.eligibile_on_criteria + self.eligibile_on_status

    @property
    def noteligible_total(self):
        return self.noteligibile_on_criteria + self.noteligibile_on_status

    @property
    def criteria_total(self):
        return self.eligibile_on_criteria + self.noteligibile_on_criteria

    @property
    def status_total(self):
        return self.eligibile_on_status + self.noteligibile_on_status


def get_trial_location_count(relevant_nct_ids, clb_open_nct_ids, current_metric):
    only_relevant_trials_outside_clb = len(relevant_nct_ids) > 0 and set(
        relevant_nct_ids
    ).isdisjoint(set(clb_open_nct_ids))
    only_relevant_trials_inside_clb = len(relevant_nct_ids) > 0 and (
        len(set(relevant_nct_ids) - set(clb_open_nct_ids)) == 0
    )

    if len(relevant_nct_ids) == 0:
        current_metric["None"] += 1
    elif only_relevant_trials_outside_clb:
        current_metric["Only outside CLB"] += 1
    elif only_relevant_trials_inside_clb:
        current_metric["Only in CLB"] += 1
    else:
        current_metric["Both"] += 1


def append_trial_location(metrics_dict, current_metric, tool, criterium):
    for metric_name, metric_value in current_metric.items():
        metrics_dict["metric_name"].append(metric_name)
        metrics_dict["criterium"].append(criterium)
        metrics_dict["tool"].append(tool)
        metrics_dict["value"].append(metric_value)


def main(formatted_data: pd.DataFrame):

    # ---------------------------------------- Nb trials ----------------------------------------

    nb_all_trials_retrieved = len(set(sum(formatted_data["nct_id"], [])))
    print("\nTotal number of clinical trials : ", nb_all_trials_retrieved)

    nb_trials_dict = {
        "metric_name": [],
        "tool": [],
        "patient_id": [],
        "value": [],
    }

    counting_metrics = [NbTrials(), NbTrialsWhenNotZero()]

    for tool in TrialMatchingTools.all():

        for _, patient_row in formatted_data.iterrows():
            ranking = patient_row[tool]

            for metric in counting_metrics:
                current_score = metric.compute(ranking=ranking)

                append_metrics_dict(
                    metrics_dict=nb_trials_dict,
                    metric=metric,
                    score=current_score,
                    patient_id=patient_row["patient_id"],
                    tool=tool,
                )

    df_nb_trials = pd.DataFrame(nb_trials_dict)

    aggregation_metrics = (
        pd.concat(
            [
                df_nb_trials.groupby(["metric_name", "tool"])["value"]
                .agg(["mean", "median", "std", "count", "sum"])
                .reset_index(),
                df_nb_trials.groupby("metric_name")["value"]
                .agg(["mean", "median", "std", "count", "sum"])
                .reset_index(),
            ]
        )
        .fillna({"tool": "all"})
        .rename(columns={"count": "patient_count", "sum": "trial_count"})
        .astype({"median": int, "trial_count": int, "patient_count": int})
        .reset_index(drop=True)
    )

    file_path = PLOTS_FOLDER / f"nb_trials_per_patient.png"
    dfi_export_proxy(
        aggregation_metrics.round({"mean": 2, "std": 2}),
        file_path,
    )

    plot_nb_trials_hist(df_nb_trials[df_nb_trials["metric_name"] == NbTrials.name])

    # --------------------------------- nb Patient / Trials annotations -----------------------------

    annotation_count = PatientTrialAnnotationCount.from_df(formatted_data)

    patient_trial_metrics = pd.DataFrame(
        {
            "Patient / Trials": ["Criteria", "Status", "Criteria and Status"],
            "Eligible": [
                f"{annotation_count.eligibile_on_criteria} ({round(annotation_count.eligibile_on_criteria_proportion, 1)}%)",
                f"{annotation_count.eligibile_on_status} ({round(annotation_count.eligibile_on_status_proportion, 1)}%)",
                annotation_count.eligible_total,
            ],
            "Not Eligible": [
                f"{annotation_count.noteligibile_on_criteria} ({round(annotation_count.noteligibile_on_criteria_proportion, 1)}%)",
                f"{annotation_count.noteligibile_on_status} ({round(annotation_count.noteligibile_on_status_proportion, 1)}%)",
                annotation_count.noteligible_total,
            ],
            "Total": [
                annotation_count.criteria_total,
                annotation_count.status_total,
                annotation_count.total,
            ],
        },
    ).set_index("Patient / Trials")

    dfi_export_proxy(
        patient_trial_metrics,
        PLOTS_FOLDER / f"Patient_Trials_Annotation_Count.png",
    )

    # ---------------------------- Number of relevant trials out of CLB ----------------------------

    nb_out_of_clb_trials_dict = {
        "metric_name": [],
        "criterium": [],
        "tool": [],
        "patient_id": [],
        "value": [],
    }

    for criterium in CRITERIA:
        clb_open_nct_ids = preprocess_clb_clinical_trials(criterium=criterium)
        for tool in TrialMatchingTools.all():
            for _, patient_row in formatted_data.iterrows():
                patient_id = patient_row["patient_id"]
                ranking = patient_row[tool]
                relevance = patient_row[criterium]
                nct_ids = patient_row["nct_id"]

                nb_out_of_clb_relevant_trials = PercentageOutOfCLBTrials().compute(
                    ranking, relevance, nct_ids, clb_open_nct_ids
                )

                append_metrics_dict(
                    metrics_dict=nb_out_of_clb_trials_dict,
                    metric=PercentageOutOfCLBTrials,
                    score=nb_out_of_clb_relevant_trials,
                    criterium=criterium,
                    tool=tool,
                    patient_id=patient_id,
                )

    df_nb_out_of_clb_trials = pd.DataFrame(nb_out_of_clb_trials_dict)

    aggregation_metrics = pd.concat(
        [
            df_nb_out_of_clb_trials.groupby(["criterium", "tool"])["value"]
            .agg(["mean", "median", "std", "count"])
            .reset_index(),
            df_nb_out_of_clb_trials.groupby("criterium")["value"]
            .agg(["mean", "median", "std", "count"])
            .reset_index(),
        ]
    ).fillna("all")

    file_path = PLOTS_FOLDER / f"nb_out_of_clb_relevant_trials.png"
    dfi_export_proxy(aggregation_metrics.round(2), file_path)

    # ------------------------ Number of patient with regard to trials out of CLB or oustide --------------------------

    nb_patient_depending_on_trials_locations = {
        "metric_name": [],
        "criterium": [],
        "tool": [],
        "value": [],
    }

    trials_locations_patient_count = {
        "None": 0,
        "Only in CLB": 0,
        "Only outside CLB": 0,
        "Both": 0,
    }

    for criterium in CRITERIA:
        clb_open_nct_ids = preprocess_clb_clinical_trials(criterium=criterium)
        for tool in TrialMatchingTools.all():
            current_metric = trials_locations_patient_count.copy()
            for _, patient_row in formatted_data.iterrows():
                rankings = patient_row[tool]
                relevances = patient_row[criterium]
                nct_ids = patient_row["nct_id"]

                relevant_nct_ids = [
                    nct_id
                    for nct_id, relevance, rank in zip(nct_ids, relevances, rankings)
                    if relevance == 1 and rank > 0
                ]
                get_trial_location_count(
                    relevant_nct_ids, clb_open_nct_ids, current_metric
                )

            append_trial_location(
                nb_patient_depending_on_trials_locations,
                current_metric,
                tool,
                criterium,
            )

        current_metric = trials_locations_patient_count.copy()
        for _, patient_row in formatted_data.iterrows():
            relevances = patient_row[criterium]
            nct_ids = patient_row["nct_id"]

            relevant_nct_ids = [
                nct_id
                for nct_id, relevance in zip(nct_ids, relevances)
                if relevance == 1
            ]
            get_trial_location_count(relevant_nct_ids, clb_open_nct_ids, current_metric)

        append_trial_location(
            nb_patient_depending_on_trials_locations, current_metric, "all", criterium
        )

    nb_patient_depending_on_trials_locations_aggregations = pd.DataFrame(
        nb_patient_depending_on_trials_locations
    )
    file_path = PLOTS_FOLDER / f"nb_patient_depending_on_trials_locations.png"
    dfi_export_proxy(
        nb_patient_depending_on_trials_locations_aggregations.round(2), file_path
    )


if __name__ == "__main__":
    formatted_data = get_formatted_data(FORMATTED_CSV_PATH)
    main(formatted_data)
