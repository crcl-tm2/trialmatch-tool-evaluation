import plotly.express as px

CRITERIA = ["eligibility", "status", "eligibility_and_status"]


class TrialMatchingTools:
    DigitalECMT = "DigitalECMT"
    Klineo = "Klineo"
    Trialing = "Trialing"
    ScreenAct = "ScreenAct"

    @classmethod
    def all(cls):
        return [
            cls.DigitalECMT,
            cls.Klineo,
            cls.Trialing,
            cls.ScreenAct,
        ]


K_VALUES = [3, 5, 10]
STRATEGY = None
CORPUS_CARDINALITY = 85326

DISPLAYED_CRITERIA = {
    "eligibility": "Eligibility",
    "status": "Status",
    "eligibility_and_status": "Eligibility and status",
}

TUMOR_TYPES_TRANSLATION = {
    "DIGESTIF": "GASTROINTESTINAL",
    "MAMMAIRE": "BREAST",
    "SARCOMES": "SARCOMA",
    "GYNECOLOGIQUE": "GYNECOLOGICAL",
    "UROLOGIE": "UROLOGICAL",
    "PROSTATE & CANCERS MASCULINS": "PROSTATE & MALE CANCERS",
    "DERMATOLOGIQUE": "DERMATOLOGICAL",
    "NEUROLOGIQUE": "NEUROLOGICAL",
    "ENDOCRINOLOGIQUE & NEUROENDOCRINE": "ENDOCRINOLOGICAL & NEUROENDOCRINE",
    "PRIMITIF INCONNU": "UNKNOWN PRIMARY ORIGIN",
    "THORACIQUE": "THORACIC",
    "TÊTE & COU": "HEAD & NECK",
    "all": "all",
}

UNIQUE_CRITERIA_CATEGORIES = [
    "Localisation",
    "Statut",
    "Cancer Type",
    "Number of previous lines",
    "Treatments of previous lines",
    "Other malignancy",
    "Residual toxicities",
    "Age",
    "Gene variant",
    "Progression under a specific treatment",
    "Performance status",
    "Unstable CNS metasases",
    "Medical history / comorbidities",
    "Wrong mutation/alteration",
    "No specific alteration",
    "Other concurrent alteration",
    "Metastases / Stage of Cancer",
]


PLOT_COLORS = list(px.colors.qualitative.Set2 + px.colors.qualitative.Pastel)
