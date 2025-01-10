from trialmatch_tool_evaluation import FORMATTED_CSV_PATH
from trialmatch_tool_evaluation.compute_metrics import main as compute_metrics
from trialmatch_tool_evaluation.correlations import main as compute_correlations
from trialmatch_tool_evaluation.error_analysis import main as compute_error_analyis
from trialmatch_tool_evaluation.molecular_alterations_stats import (
    main as compute_molecular_alteration_analysis,
)
from trialmatch_tool_evaluation.nb_trials_stats import main as compute_nb_trials_stats
from trialmatch_tool_evaluation.plot_metrics import main as plot_metrics
from trialmatch_tool_evaluation.preprocess_files import get_formatted_data
from trialmatch_tool_evaluation.statistical_tests import main as compute_ttests
from trialmatch_tool_evaluation.wrong_status_trials_stats import (
    main as compute_wrongs_status_stats,
)

if __name__ == "__main__":
    print("Starting ...")

    formatted_data = get_formatted_data(FORMATTED_CSV_PATH)
    df_metrics, df_aggregation_metrics = compute_metrics(formatted_data=formatted_data)

    compute_nb_trials_stats(formatted_data=formatted_data)
    compute_error_analyis(formatted_data=formatted_data)
    compute_molecular_alteration_analysis(formatted_data=formatted_data)
    compute_wrongs_status_stats(formatted_data=formatted_data)
    compute_ttests(df_metrics=df_metrics)
    compute_correlations(df_metrics=df_metrics)
    plot_metrics(df_metrics=df_metrics, df_aggregation_metrics=df_aggregation_metrics)

    print("Success !")
