import re
from pathlib import Path

import pandas as pd


REPORT_FILE = Path(__file__).resolve().parents[1] / "data" / "clusters_report.txt"
CLUSTER_ROW = re.compile(
    r"^\s*(\d+)\s+(\d+)\s+(\d+,\d+)\s*%\s+(.+?)\s*$"
)


def build_cluster_dataframe():
    records = []
    current_record = None

    with REPORT_FILE.open(encoding="utf-8") as report:
        for line in report:
            text = line.strip()
            if not text:
                continue

            match = CLUSTER_ROW.match(line)
            if match:
                if current_record is not None:
                    records.append(current_record)
                cluster, keyword_count, percentage, first_keywords = match.groups()
                current_record = {
                    "cluster": int(cluster),
                    "cantidad_de_palabras_clave": int(keyword_count),
                    "porcentaje_de_palabras_clave": float(
                        percentage.replace(",", ".")
                    ),
                    "keyword_lines": [first_keywords],
                }
            elif current_record is not None:
                current_record["keyword_lines"].append(text)

    if current_record is not None:
        records.append(current_record)
    if not records:
        raise ValueError(f"No se encontraron clústeres en {REPORT_FILE}.")

    rows = []
    for record in records:
        keywords = " ".join(" ".join(record["keyword_lines"]).split()).rstrip(".")
        rows.append(
            {
                "cluster": record["cluster"],
                "cantidad_de_palabras_clave": record[
                    "cantidad_de_palabras_clave"
                ],
                "porcentaje_de_palabras_clave": record[
                    "porcentaje_de_palabras_clave"
                ],
                "principales_palabras_clave": keywords,
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "cluster",
            "cantidad_de_palabras_clave",
            "porcentaje_de_palabras_clave",
            "principales_palabras_clave",
        ],
    )
