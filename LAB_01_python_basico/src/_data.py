import csv
import gzip
from datetime import datetime
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def _parse_metrics(value):
    metrics = []
    for pair in value.split(","):
        key, separator, raw_number = pair.partition(":")
        key = key.strip().lower()
        raw_number = raw_number.strip()
        if not separator or not key or not raw_number:
            raise ValueError(f"Par métrico inválido: {pair!r}")
        metrics.append((key, int(raw_number)))
    return metrics


def load_clean_data():
    records = []
    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as source:
        for line_number, row in enumerate(csv.reader(source, delimiter="\t"), start=1):
            if len(row) != 5:
                raise ValueError(
                    f"Registro {line_number}: se esperaban 5 columnas y hay {len(row)}."
                )

            letter, raw_value, raw_date, raw_codes, raw_metrics = (
                field.strip() for field in row
            )
            if not all((letter, raw_value, raw_date, raw_codes, raw_metrics)):
                raise ValueError(f"Registro {line_number}: hay campos vacíos.")

            try:
                value = int(raw_value)
            except ValueError as error:
                raise ValueError(
                    f"Registro {line_number}: valor numérico inválido."
                ) from error

            date_parts = raw_date.split("-")
            if (
                len(date_parts) != 3
                or tuple(map(len, date_parts)) != (4, 2, 2)
                or not all(part.isdigit() for part in date_parts)
            ):
                raise ValueError(f"Registro {line_number}: formato de fecha inválido.")
            year, month, day = map(int, date_parts)
            if year < 1 or not 1 <= month <= 12 or not 1 <= day <= 31:
                raise ValueError(f"Registro {line_number}: fecha fuera de rango.")

            try:
                datetime.strptime(raw_date, "%Y-%m-%d")
                date_is_valid = True
            except ValueError:
                date_is_valid = False

            codes = [code.strip().lower() for code in raw_codes.split(",")]
            if not all(codes):
                raise ValueError(f"Registro {line_number}: hay códigos vacíos.")

            try:
                metrics = _parse_metrics(raw_metrics)
            except ValueError as error:
                raise ValueError(
                    f"Registro {line_number}: métricas inválidas."
                ) from error

            records.append(
                {
                    "letter": letter.strip().upper(),
                    "value": value,
                    "date_text": raw_date,
                    "month": month,
                    "date_is_valid": date_is_valid,
                    "codes": codes,
                    "metrics": metrics,
                }
            )
    return records
