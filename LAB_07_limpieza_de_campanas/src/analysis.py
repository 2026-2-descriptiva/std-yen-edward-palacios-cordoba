from pathlib import Path

import pandas as pd


ACTIVITY_DIRECTORY = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = ACTIVITY_DIRECTORY / "data"
SUBMISSION_DIRECTORY = ACTIVITY_DIRECTORY / "submission"
SOURCE_PATTERN = "bank-marketing-campaing-*.csv.gz"

SOURCE_COLUMNS = [
    "client_id",
    "age",
    "job",
    "marital",
    "education",
    "credit_default",
    "mortgage",
    "month",
    "day",
    "contact_duration",
    "number_contacts",
    "previous_campaign_contacts",
    "previous_outcome",
    "cons_price_idx",
    "euribor_three_months",
    "campaign_outcome",
]
MONTH_NUMBERS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def build_clean_tables():
    files = sorted(DATA_DIRECTORY.glob(SOURCE_PATTERN))
    if not files:
        raise FileNotFoundError(
            f"No se encontraron archivos con el patrón {SOURCE_PATTERN}."
        )

    frames = []
    for path in files:
        frame = pd.read_csv(path, compression="gzip")
        index_columns = [
            column
            for column in frame.columns
            if str(column).startswith("Unnamed:")
        ]
        frame = frame.drop(columns=index_columns)
        if frame.columns.tolist() != SOURCE_COLUMNS:
            raise ValueError(f"El esquema de columnas no coincide en {path.name}.")
        frames.append(frame)

    data = (
        pd.concat(frames, ignore_index=True)
        .sort_values("client_id", kind="stable")
        .reset_index(drop=True)
    )
    if data["client_id"].duplicated().any():
        raise ValueError("Los archivos contienen client_id duplicados.")

    client = data[
        [
            "client_id",
            "age",
            "job",
            "marital",
            "education",
            "credit_default",
            "mortgage",
        ]
    ].copy()
    client["job"] = (
        client["job"]
        .str.replace(".", "", regex=False)
        .str.replace("-", "_", regex=False)
    )
    client["education"] = (
        client["education"].str.replace(".", "_", regex=False).replace("unknown", pd.NA)
    )
    for column in ("credit_default", "mortgage"):
        client[column] = client[column].eq("yes").astype("int64")

    campaign = data[
        [
            "client_id",
            "number_contacts",
            "contact_duration",
            "previous_campaign_contacts",
            "previous_outcome",
            "campaign_outcome",
            "month",
            "day",
        ]
    ].copy()
    campaign["previous_outcome"] = campaign["previous_outcome"].eq("success").astype(
        "int64"
    )
    campaign["campaign_outcome"] = campaign["campaign_outcome"].eq("yes").astype(
        "int64"
    )
    month = campaign.pop("month").map(MONTH_NUMBERS)
    if month.isna().any():
        raise ValueError("Se encontró un mes de contacto desconocido.")
    day = campaign.pop("day")
    contact_date = pd.to_datetime(
        pd.DataFrame(
            {
                "year": 2022,
                "month": month.astype("int64"),
                "day": day,
            }
        ),
        errors="raise",
    )
    campaign["last_contact_date"] = contact_date.dt.strftime("%Y-%m-%d")
    campaign = campaign[
        [
            "client_id",
            "number_contacts",
            "contact_duration",
            "previous_campaign_contacts",
            "previous_outcome",
            "campaign_outcome",
            "last_contact_date",
        ]
    ]

    economics = data[
        ["client_id", "cons_price_idx", "euribor_three_months"]
    ].copy()
    return client, campaign, economics
