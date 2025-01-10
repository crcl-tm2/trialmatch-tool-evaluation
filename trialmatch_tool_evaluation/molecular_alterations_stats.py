import statistics

import pandas as pd
import plotly.express as px

from trialmatch_tool_evaluation import PLOTS_FOLDER
from trialmatch_tool_evaluation.constants import PLOT_COLORS
from trialmatch_tool_evaluation.patient_data import PatientData


def get_patient_alterations(genes_string):
    if genes_string is None:
        return []
    else:
        return genes_string.split(" and ")


def plot_total_alterations(df_alterations):

    unique_alterations = df_alterations["alteration"].unique()
    frequency, text = [], []
    for alt in unique_alterations:
        freq = len(df_alterations[df_alterations["alteration"] == alt])
        frequency.append(freq)
        rate = round(freq / len(unique_alterations) * 100, 1)
        text.append(f"{freq} ({rate} %)")
    alt_stats = pd.DataFrame(
        {
            "Alteration": unique_alterations,
            "Frequency": frequency,
            "text": text,
        }
    )
    alt_stats = alt_stats.sort_values(by="Frequency", ascending=False).iloc[:12]

    colors = {
        alt_stats["Alteration"].iloc[k]: PLOT_COLORS[k] for k in range(len(alt_stats))
    }
    fig = px.bar(
        alt_stats.sort_values(by="Frequency", ascending=False),
        x="Frequency",
        y="Alteration",
        text="text",
        color="Alteration",
        orientation="h",
        title="12 most frequent molecular alterations",
        color_discrete_map=colors,
    )
    fig.write_image(PLOTS_FOLDER / "molecular_alterations.png")


def plot_patient_level_alterations(df_alterations):

    unique_patients = df_alterations["patient_id"].unique()
    unique_alterations = df_alterations["alteration"].unique()

    frequency, text = [], []

    for alt in unique_alterations:
        freq = 0
        for p in unique_patients:
            if (
                alt
                in df_alterations[df_alterations["patient_id"] == p][
                    "alteration"
                ].tolist()
            ):
                freq += 1
        frequency.append(freq)
        rate = round(freq / len(unique_patients) * 100, 1)
        text.append(f"{freq} ({rate} %)")

    alt_stats = pd.DataFrame(
        {"Alteration": unique_alterations, "Frequency": frequency, "text": text}
    )
    alt_stats = alt_stats.sort_values(by="Frequency", ascending=False).iloc[:12]

    colors = {
        alt_stats["Alteration"].iloc[k]: PLOT_COLORS[k] for k in range(len(alt_stats))
    }
    fig = px.bar(
        alt_stats.sort_values(by="Frequency", ascending=False),
        x="Frequency",
        y="Alteration",
        text="text",
        color="Alteration",
        orientation="h",
        title="12 most frequent molecular alterations (rate over patients)",
        color_discrete_map=colors,
    )
    fig.update_xaxes(title_text="Number of patients")
    fig.write_image(PLOTS_FOLDER / "molecular_alterations_patient_level.png")


def main(formatted_data: pd.DataFrame):
    PLOTS_FOLDER.mkdir(exist_ok=True)

    # Find patients molecular alterations
    data = {"patient_id": [], "alteration": []}

    for _, patient_values in formatted_data.iterrows():
        patient_data = PatientData.from_ranking(patient_values.to_dict())
        alterations = get_patient_alterations(patient_data.genes)

        for alteration in alterations:
            data["patient_id"].append(patient_data.patient_id)
            data["alteration"].append(alteration)

    df_alterations = pd.DataFrame(data)
    print("Total number of alterations : ", len(df_alterations))

    # Plot alterations rate
    plot_total_alterations(df_alterations)
    plot_patient_level_alterations(df_alterations)

    # Compute mean number of alterations per patient
    unique_patients = df_alterations["patient_id"].unique()
    nb_alterations = []
    for p in unique_patients:
        nb_alterations.append(len(df_alterations[df_alterations["patient_id"] == p]))
    mean = round(statistics.mean(nb_alterations), 2)
    std = round(statistics.stdev(nb_alterations), 2)
    print(f"Mean number of alterations per patient : {mean} (sd {std})")


if __name__ == "__main__":
    main()
