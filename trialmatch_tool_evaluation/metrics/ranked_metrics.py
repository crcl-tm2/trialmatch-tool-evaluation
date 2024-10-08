import math

from trialmatch_tool_evaluation.constants import CORPUS_CARDINALITY
from trialmatch_tool_evaluation.metrics.base_metrics import RankedMetric


class FN_at_k(RankedMetric):
    generic_name = "FN@{k}"

    def __init__(self, k):
        super().__init__(k=k)

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        value = len(
            [
                i
                for i in range(len(relevance))
                if (ranking[i] == 0 or ranking[i] > self.k) and relevance[i] == 1
            ]
        )
        return value


class TP_at_k(RankedMetric):
    generic_name = "TP@{k}"

    def __init__(self, k):
        super().__init__(k=k)

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        value = len(
            [
                i
                for i in range(len(relevance))
                if ranking[i] > 0 and ranking[i] <= self.k and relevance[i] == 1
            ]
        )
        return value


class FP_at_k(RankedMetric):
    generic_name = "FP@{k}"

    def __init__(self, k):
        super().__init__(k=k)

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        value = len(
            [
                i
                for i in range(len(relevance))
                if ranking[i] > 0 and ranking[i] <= self.k and relevance[i] == 0
            ]
        )
        return value


class TN_at_k(RankedMetric):
    generic_name = "TN@{k}"

    def __init__(self, k):
        super().__init__(k=k)

    def __init__(self, k=3, corpus_cardinality=80000):
        super().__init__(k=k)
        self.corpus_cardinality = corpus_cardinality

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        tp = TP_at_k(k=self.k).compute(ranking, relevance)
        fp = FP_at_k(k=self.k).compute(ranking, relevance)
        fn = FN_at_k(k=self.k).compute(ranking, relevance)

        value = self.corpus_cardinality - tp - fp - fn
        return value


class Precision_at_k(RankedMetric):
    generic_name = "Precision@{k}"

    def __init__(self, k, strategy=None):
        super().__init__(k=k)
        self.strategy = strategy

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        if sum(relevance) == 0:
            return self.strategy

        if sum(ranking) == 0:
            return 0.0

        tp = TP_at_k(k=self.k).compute(ranking, relevance)
        fp = FP_at_k(k=self.k).compute(ranking, relevance)
        value = tp / (tp + fp)

        return value


class Sensitivity_at_k(RankedMetric):
    generic_name = "Sensibility@{k}"

    def __init__(self, k, strategy=None):
        super().__init__(k=k)
        self.strategy = strategy

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        if sum(relevance) == 0:
            return self.strategy

        tp = TP_at_k(k=self.k).compute(ranking, relevance)
        fn = FN_at_k(k=self.k).compute(ranking, relevance)

        value = tp / (tp + fn)
        return value


class Specificity_at_k(RankedMetric):
    name = "Specificity@k"

    def __init__(self, k, corpus_cardinality):
        super().__init__(k=k)
        self.corpus_cardinality = corpus_cardinality

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        tp = TP_at_k(k=self.k).compute(ranking, relevance)
        fp = FP_at_k(k=self.k).compute(ranking, relevance)
        fn = FN_at_k(k=self.k).compute(ranking, relevance)
        tn = self.corpus_cardinality - tp - fn - fp

        return tn / (tn + fp)


class AP_at_k(RankedMetric):
    generic_name = "AP@{k}"

    def __init__(self, k, strategy=None):
        super().__init__(k=k)
        self.strategy = strategy

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        if sum(relevance) == 0:
            return self.strategy

        if sum(ranking) == 0:
            return 0.0

        precisions_sum = 0
        nb_relevant = 0
        for i in range(1, min(self.k, max(ranking)) + 1):
            prec = Precision_at_k(k=i, strategy=self.strategy).compute(
                ranking, relevance
            )
            rel = relevance[ranking.index(i)]
            nb_relevant += rel
            precisions_sum += prec * rel

        if nb_relevant == 0:
            return precisions_sum

        return precisions_sum / nb_relevant


class NDCG_at_k(RankedMetric):
    generic_name = "NDCG@{k}"

    def __init__(self, k, strategy=None):
        super().__init__(k=k)
        self.strategy = strategy

    def discount(self, x):
        return math.log(x + 1, 2)

    def dcg(self, ranking, relevance):
        dcg = []
        for i in range(len(relevance)):
            if ranking[i] == 0 or relevance[i] == 0:
                dcg.append(0)
            else:
                dcg.append(relevance[i] / self.discount(ranking[i]))
        return dcg

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        if sum(relevance) == 0:
            return self.strategy

        if sum(ranking) == 0:
            return 0.0

        dcg = self.dcg(ranking, relevance)
        sum_dcg = sum([dcg[i] for i in range(len(relevance)) if ranking[i] <= self.k])

        if sum_dcg == 0:
            return 0.0

        ideal_ranking = range(1, max(1, min(self.k, sum(relevance))) + 1)
        ideal_dcg = sum([1 / self.discount(i) for i in ideal_ranking])
        value = sum_dcg / ideal_dcg

        return value


class NFPR_at_k(RankedMetric):
    generic_name = "NFPR@{k}"
    corpus_cardinality = CORPUS_CARDINALITY

    def __init__(self, k, strategy=None):
        super().__init__(k=k)
        self.strategy = strategy

    def false_positive_rate(self, ranking, relevance):
        tp = TP_at_k(k=self.k).compute(ranking, relevance)
        fp = FP_at_k(k=self.k).compute(ranking, relevance)
        fn = FN_at_k(k=self.k).compute(ranking, relevance)

        return fp / (self.corpus_cardinality - tp - fn)

    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ):
        fpr = self.false_positive_rate(ranking, relevance)
        worst_score = self.k / (self.corpus_cardinality - self.k)
        value = fpr / worst_score

        return value
