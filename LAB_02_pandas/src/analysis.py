from pathlib import Path

import pandas as pd


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"


def _read_table(filename, expected_columns, text_columns, numeric_columns):
    table = pd.read_csv(DATA_DIRECTORY / filename, sep="\t")
    if table.columns.tolist() != expected_columns:
        raise ValueError(
            f"{filename}: se esperaban las columnas {expected_columns}, "
            f"se encontraron {table.columns.tolist()}."
        )
    if table.isna().any().any():
        raise ValueError(f"{filename}: la tabla contiene valores vacíos.")

    for column in text_columns:
        table[column] = table[column].str.strip()
    for column in numeric_columns:
        values = pd.to_numeric(table[column], errors="raise")
        if (values % 1 != 0).any():
            raise ValueError(f"{filename}: {column} debe contener enteros.")
        table[column] = values.astype("int64")
    return table


def load_tables():
    return {
        "tbl0": _read_table(
            "tbl0.tsv",
            ["c0", "c1", "c2", "c3"],
            ["c1", "c3"],
            ["c0", "c2"],
        ),
        "tbl1": _read_table(
            "tbl1.tsv",
            ["c0", "c4"],
            ["c4"],
            ["c0"],
        ),
        "tbl2": _read_table(
            "tbl2.tsv",
            ["c0", "c5a", "c5b"],
            ["c5a"],
            ["c0", "c5b"],
        ),
    }


def analyze_tables(tables):
    tbl0 = tables["tbl0"]
    tbl1 = tables["tbl1"]
    tbl2 = tables["tbl2"]

    grouped = tbl0.groupby("c1", sort=True)
    values_by_category = grouped["c2"]

    combined_tbl2 = tbl2.assign(
        c5=tbl2["c5a"] + ":" + tbl2["c5b"].astype(str)
    )
    merged = tbl0.merge(tbl2, on="c0", how="inner", validate="one_to_many")

    return {
        "01": len(tbl0),
        "02": tbl0.shape[1],
        "03": grouped.size(),
        "04": values_by_category.mean(),
        "05": values_by_category.max(),
        "06": sorted(tbl1["c4"].str.upper().unique().tolist()),
        "07": values_by_category.sum(),
        "08": tbl0.assign(suma=tbl0["c0"] + tbl0["c2"]),
        "09": tbl0.assign(year=tbl0["c3"].str.slice(0, 4)),
        "10": values_by_category.agg(
            lambda values: ":".join(map(str, sorted(values.tolist())))
        ).to_frame(),
        "11": (
            tbl1.groupby("c0", as_index=False, sort=True)
            .agg(c4=("c4", lambda values: ",".join(sorted(values))))
        ),
        "12": (
            combined_tbl2.groupby("c0", sort=True)["c5"]
            .agg(lambda values: ",".join(sorted(values)))
            .reset_index()
        ),
        "13": merged.groupby("c1", sort=True)["c5b"].sum(),
    }


def analyze_all():
    return analyze_tables(load_tables())


def answer(number):
    return analyze_all()[number]
