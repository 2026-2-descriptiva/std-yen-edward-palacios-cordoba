import json
import re
from pathlib import Path

import pandas as pd


ACTIVITY_DIRECTORY = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIRECTORY / "data" / "ventas.csv.gz"
SUBMISSION_DIRECTORY = ACTIVITY_DIRECTORY / "submission"
REPORT_FILE = SUBMISSION_DIRECTORY / "data_quality_report.json"

REQUIRED_COLUMNS = {
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s.]+(?:\.[^@\s.]+)+$")


def _normalize_header(header):
    cleaned = str(header).replace("\ufeff", "").strip().lower()
    return "_".join(cleaned.split())


def _missing_mask(values):
    return values.eq("") | values.str.strip().str.upper().eq("N/A")


def build_quality_report():
    data = pd.read_csv(
        DATA_FILE,
        compression="gzip",
        encoding="utf-8",
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )
    data.columns = [_normalize_header(column) for column in data.columns]
    columns = set(data.columns)

    missing_value_count_by_column = {
        column: int(_missing_mask(data[column]).sum()) for column in data.columns
    }

    duplicate_supplier_id_row_count = 0
    if "supplier_id" in columns:
        supplier_ids = data.loc[
            ~_missing_mask(data["supplier_id"]), "supplier_id"
        ]
        duplicate_supplier_id_row_count = int(
            supplier_ids.duplicated(keep=False).sum()
        )

    invalid_email_count = 0
    if "contact_email" in columns:
        emails = data.loc[~_missing_mask(data["contact_email"]), "contact_email"]
        invalid_email_count = int(
            (~emails.map(lambda email: bool(EMAIL_PATTERN.fullmatch(email)))).sum()
        )

    invalid_unit_count = 0
    if "units" in columns:
        units = data.loc[~_missing_mask(data["units"]), "units"]
        numeric_units = pd.to_numeric(units, errors="coerce")
        invalid_units = (
            numeric_units.isna()
            | numeric_units.le(0)
            | numeric_units.mod(1).ne(0)
        )
        invalid_unit_count = int(invalid_units.sum())

    report = {
        "row_count": int(len(data)),
        "column_count": int(data.shape[1]),
        "missing_required_columns": sorted(REQUIRED_COLUMNS - columns),
        "unexpected_columns": sorted(columns - REQUIRED_COLUMNS),
        "duplicate_row_count": int(data.duplicated().sum()),
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": (
            sorted(data["country"].unique().tolist()) if "country" in columns else []
        ),
    }

    SUBMISSION_DIRECTORY.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
