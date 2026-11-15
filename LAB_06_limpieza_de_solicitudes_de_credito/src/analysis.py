import unicodedata
from pathlib import Path

import pandas as pd


ACTIVITY_DIRECTORY = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIRECTORY / "data" / "solicitudes_de_credito.csv.gz"
SUBMISSION_DIRECTORY = ACTIVITY_DIRECTORY / "submission"
OUTPUT_FILE = SUBMISSION_DIRECTORY / "solicitudes_de_credito.csv"

COLUMNS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "estrato",
    "comuna_ciudadano",
    "fecha_de_beneficio",
    "monto_del_credito",
    "línea_credito",
]
TEXT_COLUMNS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "línea_credito",
]
REQUIRED_COLUMNS = [column for column in COLUMNS if column != "comuna_ciudadano"]


def _normalize_text(value):
    if pd.isna(value):
        return value
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    text = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )
    return " ".join(text.replace("-", " ").split())


def build_clean_dataset():
    data = pd.read_csv(
        DATA_FILE,
        sep=";",
        compression="gzip",
        encoding="utf-8-sig",
    )
    index_columns = [
        column for column in data.columns if str(column).startswith("Unnamed:")
    ]
    data = data.drop(columns=index_columns)
    data.columns = [str(column).strip() for column in data.columns]

    missing_columns = sorted(set(COLUMNS) - set(data.columns))
    unexpected_columns = sorted(set(data.columns) - set(COLUMNS))
    if missing_columns or unexpected_columns:
        raise ValueError(
            f"Columnas inesperadas en el archivo: faltantes={missing_columns}, "
            f"no reconocidas={unexpected_columns}."
        )
    data = data[COLUMNS].copy()

    for column in TEXT_COLUMNS:
        data[column] = data[column].map(_normalize_text).replace("", pd.NA)

    dates = pd.to_datetime(
        data["fecha_de_beneficio"], format="%d/%m/%Y", errors="coerce"
    )
    for date_format in ("%Y-%m-%d", "%Y/%m/%d"):
        dates = dates.fillna(
            pd.to_datetime(
                data["fecha_de_beneficio"],
                format=date_format,
                errors="coerce",
            )
        )
    if dates.isna().any():
        raise ValueError("Hay fechas de beneficio que no se pudieron interpretar.")
    data["fecha_de_beneficio"] = dates.dt.strftime("%Y-%m-%d")

    strata = pd.to_numeric(data["estrato"], errors="raise")
    if strata.isna().any() or strata.mod(1).ne(0).any():
        raise ValueError("La columna estrato debe contener números enteros.")
    data["estrato"] = strata.astype("int64")

    amounts = (
        data["monto_del_credito"]
        .astype("string")
        .str.strip()
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(r"\.0+$", "", regex=True)
    )
    amounts = pd.to_numeric(amounts, errors="raise")
    if amounts.isna().any() or amounts.mod(1).ne(0).any():
        raise ValueError("El monto del crédito debe ser un número entero.")
    data["monto_del_credito"] = amounts.astype("int64")

    communes = pd.to_numeric(data["comuna_ciudadano"], errors="raise")
    if communes.dropna().mod(1).ne(0).any():
        raise ValueError("Los valores presentes de comuna deben ser enteros.")
    data["comuna_ciudadano"] = communes.astype("Int64")

    data = data.dropna(subset=REQUIRED_COLUMNS)
    data = data.drop_duplicates(ignore_index=True)
    return data


def write_clean_dataset():
    data = build_clean_dataset()
    SUBMISSION_DIRECTORY.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8")
    return data
