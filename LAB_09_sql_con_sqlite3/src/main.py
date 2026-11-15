import csv
import gzip
import sqlite3
from pathlib import Path


ACTIVITY_DIRECTORY = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = ACTIVITY_DIRECTORY / "data"
QUERY_DIRECTORY = Path(__file__).resolve().parent
TABLES = {
    "tbl0": "K0 CHAR(1), c01 INT, c02 INT, c03 CHAR(4), c04 FLOAT",
    "tbl1": (
        "K0 CHAR(1), K1 INT, c12 FLOAT, c13 INT, c14 DATE, "
        "c15 FLOAT, c16 CHAR(4)"
    ),
    "tbl2": "K1 INT, c21 FLOAT, c22 INT, c23 DATE, c24 FLOAT, c25 CHAR(5)",
}


def _load_tables(connection):
    for table, columns in TABLES.items():
        connection.execute(f"CREATE TABLE {table} ({columns})")
        input_file = DATA_DIRECTORY / f"{table}.csv.gz"
        with gzip.open(input_file, "rt", encoding="utf-8-sig", newline="") as source:
            rows = list(csv.reader(source))
        placeholders = ", ".join("?" for _ in rows[0])
        connection.executemany(
            f"INSERT INTO {table} VALUES ({placeholders})",
            rows,
        )


def main():
    connection = sqlite3.connect(":memory:")
    try:
        _load_tables(connection)
        for query_file in sorted(QUERY_DIRECTORY.glob("pregunta_*.sql")):
            rows = connection.execute(
                query_file.read_text(encoding="utf-8")
            ).fetchall()
            print(f"\n{query_file.stem}:")
            for row in rows:
                print(row)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
