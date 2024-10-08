from pathlib import Path
import os

ARTIFACT_FOLDER = Path(
    os.getenv("ARTIFACT_FOLDER_PATH", Path(__file__).parent.parent / "artifacts")
)

DATA_RAW_FOLDER = ARTIFACT_FOLDER / "data_raw"
PLOTS_FOLDER = ARTIFACT_FOLDER / "plots"
RESULTS_FOLDER = ARTIFACT_FOLDER / "results"

CLB_CLINICAL_TRIALS_PATH = DATA_RAW_FOLDER / "clb_clinical_trials.csv"

METRICS_PATH = RESULTS_FOLDER / "metrics.csv"
AGGREGATION_METRICS_PATH = RESULTS_FOLDER / "aggregation_metrics.csv"
FORMATTED_CSV_PATH = DATA_RAW_FOLDER / "formatted_data.csv"
