from trialmatch_tool_evaluation.metrics.base_metrics import Metric
from trialmatch_tool_evaluation.metrics.ranked_metrics import (
    FN_at_k,
    FP_at_k,
    Precision_at_k,
    Sensitivity_at_k,
    Specificity_at_k,
    TN_at_k,
    TP_at_k,
)


def get_max_rank(ranking):
    max_rank = 0
    if len(ranking) != 0:
        max_rank = max(ranking)
    return max_rank


class TN(Metric):
    name = "TN"

    def __init__(self, corpus_cardinality=80000):
        self.corpus_cardinality = corpus_cardinality

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        max_rank = get_max_rank(ranking)

        tn_at_max = TN_at_k(k=max_rank, corpus_cardinality=self.corpus_cardinality)
        return tn_at_max.compute(ranking=ranking, relevance=relevance)


class TP(Metric):
    name = "TP"

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        max_rank = get_max_rank(ranking)

        tp_at_max = TP_at_k(k=max_rank)
        return tp_at_max.compute(ranking=ranking, relevance=relevance)


class FP(Metric):
    name = "FP"

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        max_rank = get_max_rank(ranking)

        fp_at_max = FP_at_k(k=max_rank)
        return fp_at_max.compute(ranking=ranking, relevance=relevance)


class FN(Metric):
    name = "FN"

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        max_rank = get_max_rank(ranking)

        fn_at_max = FN_at_k(max_rank)
        return fn_at_max.compute(ranking=ranking, relevance=relevance)


class Precision(Metric):
    name = "Precision"

    def __init__(self, strategy=None):
        self.strategy = strategy

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        max_rank = get_max_rank(ranking)

        precision_at_max = Precision_at_k(max_rank, strategy=self.strategy)
        return precision_at_max.compute(ranking=ranking, relevance=relevance)


class Sensitivity(Metric):
    name = "Sensibility"

    def __init__(self, strategy=None):
        self.strategy = strategy

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        max_rank = get_max_rank(ranking)

        sensitivity_at_max = Sensitivity_at_k(
            k=max_rank,
            strategy=self.strategy,
        )
        return sensitivity_at_max.compute(ranking=ranking, relevance=relevance)


class Specificity(Metric):
    name = "Specificity"

    def __init__(self, corpus_cardinality=80000):
        self.corpus_cardinality = corpus_cardinality

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        max_rank = get_max_rank(ranking)

        specificity_at_max = Specificity_at_k(
            k=max_rank,
            corpus_cardinality=self.corpus_cardinality,
        )
        return specificity_at_max.compute(ranking=ranking, relevance=relevance)


class Accuracy(Metric):
    name = "Accuracy"

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        tp = TP().compute(ranking, relevance)
        fp = FP().compute(ranking, relevance)
        fn = FN().compute(ranking, relevance)
        tn = TN().compute(ranking, relevance)
        value = (tp + tn) / (tp + fp + tn + fn)
        return value


class NbTrials(Metric):
    name = "NbTrials"

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        if len(ranking) == 0:
            return 0
        value = max(ranking)
        return value


class NbTrialsWhenNotZero(Metric):
    name = "NbTrialsWhenNotZero"

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        if len(ranking) == 0:
            return None

        if max(ranking) != 0:
            return max(ranking)

        return None


class PercentageOutOfCLBTrials(Metric):
    name = "PercentageOutOfCLBTrials"

    def compute(self, ranking, relevance, nct_ids, clb_open_nct_ids):
        tp = TP().compute(ranking, relevance)
        if tp == 0:
            return 0
        nb_relevant_out_of_clb = 0
        for i, trial in enumerate(nct_ids):
            if (
                (ranking[i] != 0)
                and (relevance[i] == 1)
                and (trial not in clb_open_nct_ids)
            ):
                nb_relevant_out_of_clb += 1
        return nb_relevant_out_of_clb / tp


class NbErrors(Metric):
    name = "NbErrors"

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        nb_errors = 0
        for i in range(len(relevance)):
            if ranking[i] != 0 and relevance[i] == 0:
                nb_errors += 1

        return nb_errors


class ErrorRate(Metric):
    name = "ErrorRate"

    def __init__(self, strategy=None):
        self.strategy = strategy

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        if sum(ranking) == 0:
            return None

        nb_errors = NbErrors()
        nb_total_errors = nb_errors.compute(ranking=ranking, relevance=total_relevance)
        nb_specific_errors = nb_errors.compute(
            ranking=ranking, relevance=specific_relevance
        )

        if nb_total_errors == 0:
            return None

        return nb_specific_errors / nb_total_errors


class NbTotalTreatmentLines(Metric):
    name = "NbTotalTreatmentLines"

    def __init__(self, local_treatments_list):
        self.local_treatments_list = local_treatments_list

    def compute(self, treatment_lines):
        return len(treatment_lines)


class NbLocalTreatmentLines(Metric):
    name = "NbLocalTreatmentLines"

    def __init__(self, local_treatments_list):
        self.local_treatments_list = local_treatments_list

    def compute(self, treatment_lines):
        nb_local_lines = 0
        for i in range(len(treatment_lines)):
            for t in self.local_treatments_list:
                if t in treatment_lines[i]:
                    nb_local_lines += 1
                    break
        return nb_local_lines


class NbSystemicTreatmentLines(Metric):
    name = "NbSystemicTreatmentLines"

    def __init__(self, local_treatments_list):
        self.local_treatments_list = local_treatments_list

    def compute(self, treatment_lines):
        nb_total_lines = NbTotalTreatmentLines(self.local_treatments_list).compute(
            treatment_lines
        )
        nb_local_lines = NbLocalTreatmentLines(self.local_treatments_list).compute(
            treatment_lines
        )
        return nb_total_lines - nb_local_lines
