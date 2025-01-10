from dataclasses import dataclass

from trialmatch_tool_evaluation.constants import TrialMatchingTools


@dataclass
class PatientData:
    patient_id: int
    all_trials_retrieved: list[int]
    rankings: dict
    eligibility_values: list[int]
    status_values: list[int]
    tumor_type: str
    exclusion_category_1: list[str]
    exclusion_category_2: list[str]
    genes: str | None
    strategy_none_relevant: int | None = None
    none_relevant_eligibility: bool = False
    none_relevant_status: bool = False
    none_relevant_both: bool = False

    @property
    def nb_all_trials_retrieved(self):
        return len(self.all_trials_retrieved)

    def _update_tool_name(self, tool):
        if tool in ["klineo_before_maj", "klineo_after_maj"]:
            return "Klineo"

        return tool

    @staticmethod
    def from_ranking(patient_dict: dict):
        return PatientData(
            patient_id=patient_dict["patient_id"],
            tumor_type=patient_dict["tumor_type"],
            all_trials_retrieved=patient_dict["nct_id"],
            rankings={
                TrialMatchingTools.DigitalECMT: patient_dict[
                    TrialMatchingTools.DigitalECMT
                ],
                TrialMatchingTools.Klineo: patient_dict[TrialMatchingTools.Klineo],
                TrialMatchingTools.Trialing: patient_dict[TrialMatchingTools.Trialing],
                TrialMatchingTools.ScreenAct: patient_dict[
                    TrialMatchingTools.ScreenAct
                ],
            },
            eligibility_values=patient_dict["eligibility"],
            status_values=patient_dict["status"],
            exclusion_category_1=patient_dict["exclusion_category_1"],
            exclusion_category_2=patient_dict["exclusion_category_2"],
            genes=patient_dict["genes"],
        )

    def get_relevance(self, criteria):

        if criteria == "eligibility":
            relevance = self.eligibility_values
            if sum(relevance) == 0:
                self.none_relevant_eligibility = True
        elif criteria == "status":
            relevance = self.status_values
            if sum(relevance) == 0:
                self.none_relevant_status = True
        elif criteria == "eligibility_and_status":
            relevance = [
                (
                    1
                    if self.eligibility_values[i] == 1 and self.status_values[i] == 1
                    else 0
                )
                for i in range(self.nb_all_trials_retrieved)
            ]
            if sum(relevance) == 0:
                self.none_relevant_both = True
        else:
            raise ValueError("Unknown criteria.")

        return relevance
