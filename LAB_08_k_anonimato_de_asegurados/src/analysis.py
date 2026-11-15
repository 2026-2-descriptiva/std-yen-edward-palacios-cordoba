import json
from pathlib import Path

import pandas as pd


ACTIVITY_DIRECTORY = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIRECTORY / "data" / "insurance.csv.gz"
SUBMISSION_DIRECTORY = ACTIVITY_DIRECTORY / "submission"
REPORT_FILE = SUBMISSION_DIRECTORY / "privacy_report.json"
PUBLISHED_FILE = SUBMISSION_DIRECTORY / "insurance_published.csv"
K = 5

SCHEMES = {
    "with_children": [
        "age_group",
        "sex",
        "bmi_group",
        "children_group",
        "region",
    ],
    "without_children": ["age_group", "sex", "bmi_group", "region"],
}


def _evaluate_scheme(data, quasi_identifiers):
    class_sizes = data.groupby(
        quasi_identifiers, observed=True, dropna=False, sort=True
    ).size()
    sizes_by_record = data.groupby(
        quasi_identifiers, observed=True, dropna=False, sort=True
    )["smoker"].transform("size")
    published = data.loc[sizes_by_record.ge(K)].copy()
    published_groups = published.groupby(
        quasi_identifiers, observed=True, dropna=False, sort=True
    )
    published_class_sizes = published_groups.size()
    smoker_counts = published_groups["smoker"].nunique()
    classes_without_diversity = smoker_counts[smoker_counts.eq(1)]

    return {
        "quasi_identifiers": quasi_identifiers,
        "equivalence_classes": int(len(class_sizes)),
        "k_before_suppression": int(class_sizes.min()),
        "suppressed_records": int(sizes_by_record.lt(K).sum()),
        "published_records": int(len(published)),
        "published_classes": int(len(published_class_sizes)),
        "classes_without_smoker_diversity": int(len(classes_without_diversity)),
        "records_without_smoker_diversity": int(
            published_class_sizes.reindex(classes_without_diversity.index).sum()
        ),
    }, published


def build_privacy_outputs():
    data = pd.read_csv(DATA_FILE, compression="gzip")
    original_quasi_identifiers = ["age", "sex", "bmi", "children", "region"]
    original_class_sizes = data.groupby(
        original_quasi_identifiers, observed=True, dropna=False
    ).size()

    data = data.assign(
        age_group=pd.cut(
            data["age"],
            bins=[18, 30, 40, 50, 65],
            labels=["18-29", "30-39", "40-49", "50-64"],
            right=False,
        ),
        bmi_group=pd.cut(
            data["bmi"],
            bins=[float("-inf"), 18.5, 25, 30, float("inf")],
            labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
            right=False,
        ),
        children_group=pd.cut(
            data["children"],
            bins=[-1, 0, 2, float("inf")],
            labels=["0", "1-2", "3+"],
            right=True,
        ),
    )

    scheme_results = {}
    published_by_scheme = {}
    for name, quasi_identifiers in SCHEMES.items():
        scheme_results[name], published_by_scheme[name] = _evaluate_scheme(
            data, quasi_identifiers
        )

    selected_scheme = min(
        scheme_results,
        key=lambda name: scheme_results[name]["suppressed_records"],
    )
    published = published_by_scheme[selected_scheme]
    publication_columns = (
        SCHEMES[selected_scheme] + ["smoker", "charges"]
    )
    published = published[publication_columns]

    report = {
        "original_k": int(original_class_sizes.min()),
        "original_unique_records": int(
            original_class_sizes[original_class_sizes.eq(1)].sum()
        ),
        "schemes": scheme_results,
        "selected_scheme": selected_scheme,
        "mean_charges_original": float(data["charges"].mean()),
        "mean_charges_published": float(published["charges"].mean()),
        "smoker_rate_original": float(data["smoker"].eq("yes").mean()),
        "smoker_rate_published": float(published["smoker"].eq("yes").mean()),
    }

    return report, published


def write_privacy_outputs():
    report, published = build_privacy_outputs()
    SUBMISSION_DIRECTORY.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    published.to_csv(PUBLISHED_FILE, index=False)
    return report
