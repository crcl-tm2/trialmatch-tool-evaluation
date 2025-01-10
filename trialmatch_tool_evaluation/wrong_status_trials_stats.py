import pandas as pd

from trialmatch_tool_evaluation import FORMATTED_CSV_PATH, PLOTS_FOLDER
from trialmatch_tool_evaluation.preprocess_files import get_formatted_data

FP_trials = [
    "NCT04044768",
    "NCT02264678",
    "NCT04300556",
    "NCT04807816",
    "NCT05180474",
    "NCT04886804",
    "NCT06065748",
    "NCT05386108",
]

FN_trials = [
    "NCT03178552",
    "NCT03548428",
    "NCT05267912",
    "NCT03821935",
    "NCT04589845",
    "NCT05299840",
    "NCT05007106",
    "NCT05442749",
    "NCT05183984",
    "NCT05310643",
    "NCT05552001",
    "NCT05631249",
    "NCT05601752",
]


def append_dict(dict_object, nct, patient):
    dict_object["nct"].append(nct)
    dict_object["patient"].append(patient)
    return dict_object


def main(formatted_data: pd.DataFrame):

    FP_trials_data = {"nct": [], "patient": []}
    FN_trials_data = {"nct": [], "patient": []}

    for _, patient_row in formatted_data.iterrows():
        patient_id = patient_row["patient_id"]
        patient_trials = patient_row["nct_id"]
        for nct in FP_trials:
            if nct in patient_trials:
                append_dict(FP_trials_data, nct, patient_id)
        for nct in FN_trials:
            if nct in patient_trials:
                append_dict(FN_trials_data, nct, patient_id)

    FP_trials_df = pd.DataFrame(FP_trials_data)
    FN_trials_df = pd.DataFrame(FN_trials_data)

    FP_trials_df = FP_trials_df.sort_values(by="nct").reset_index(drop=True)
    FN_trials_df = FN_trials_df.sort_values(by="nct").reset_index(drop=True)

    FP_trials_path = PLOTS_FOLDER / "FP_CLB_trials.xlsx"
    FP_trials_df.to_csv(FP_trials_path)
    FN_trials_path = PLOTS_FOLDER / "FN_CLB_trials.xlsx"
    FN_trials_df.to_csv(FN_trials_path)


if __name__ == "__main__":
    formatted_data = get_formatted_data(FORMATTED_CSV_PATH)
    main(formatted_data)
