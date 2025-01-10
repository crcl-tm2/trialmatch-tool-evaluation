from abc import abstractmethod


class Metric:
    name: str

    @abstractmethod
    def compute(
        self,
        ranking,
        relevance=None,
        nb_all_trials_retrieved=None,
        specific_relevance=None,
        total_relevance=None,
    ) -> float:
        pass

    def __str__(self):
        return f"name: {self.name}"


class RankedMetric(Metric):
    generic_name = "my_metric_name"
    k = 0

    @property
    def name(self):
        return self.generic_name.format(k=self.k)

    def __init__(self, k):
        self.k = k
