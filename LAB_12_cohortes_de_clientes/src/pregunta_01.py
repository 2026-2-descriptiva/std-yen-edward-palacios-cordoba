from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    activity_dir = Path(__file__).resolve().parents[1]
    data_path = activity_dir / "data" / "sales.csv.gz"
    submission_dir = activity_dir / "submission"

    orders = pd.read_csv(data_path, compression="gzip")
    orders["order_month"] = pd.to_datetime(orders["OrderDate"]).dt.to_period("M")
    orders["cohort_period"] = orders.groupby("CustomerID")["order_month"].transform(
        "min"
    )
    orders["cohort_month"] = orders["cohort_period"].astype(str)
    orders["period_index"] = (
        (orders["order_month"].dt.year - orders["cohort_period"].dt.year) * 12
        + orders["order_month"].dt.month
        - orders["cohort_period"].dt.month
    )

    retention = (
        orders.groupby(["cohort_month", "period_index"], as_index=False)
        .agg(active_customers=("CustomerID", "nunique"))
        .sort_values(["cohort_month", "period_index"])
    )
    cohort_sizes = (
        retention.loc[retention["period_index"] == 0, ["cohort_month", "active_customers"]]
        .rename(columns={"active_customers": "cohort_size"})
    )
    retention = retention.merge(
        cohort_sizes, on="cohort_month", how="left", validate="many_to_one"
    )
    retention["retention_rate"] = (
        retention["active_customers"] / retention["cohort_size"]
    )
    retention["active_customers"] = retention["active_customers"].astype("int64")
    retention["cohort_size"] = retention["cohort_size"].astype("int64")
    retention = retention[
        [
            "cohort_month",
            "period_index",
            "active_customers",
            "cohort_size",
            "retention_rate",
        ]
    ]

    heatmap = retention.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )
    matrix = np.ma.masked_invalid(heatmap.to_numpy(dtype=float))
    colormap = plt.get_cmap("YlGnBu").with_extremes(bad="#eeeeee")
    figure, axis = plt.subplots(
        figsize=(max(6, heatmap.shape[1] * 0.8), max(4, heatmap.shape[0] * 0.5)),
        dpi=80,
    )
    image = axis.imshow(matrix, aspect="auto", cmap=colormap, vmin=0, vmax=1)
    axis.set_xticks(range(len(heatmap.columns)), labels=heatmap.columns)
    axis.set_yticks(range(len(heatmap.index)), labels=heatmap.index)
    axis.set_xlabel("Meses desde la primera compra")
    axis.set_ylabel("Cohorte de primera compra")
    axis.set_title("Retencion de clientes por cohorte")
    figure.colorbar(image, ax=axis, label="Retencion")

    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if not np.ma.is_masked(value):
                axis.text(
                    column_index,
                    row_index,
                    f"{value:.0%}",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=8,
                )

    figure.tight_layout()
    submission_dir.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        submission_dir / "cohort_retention_heatmap.png",
        dpi=80,
        bbox_inches="tight",
    )
    plt.close(figure)
    retention.to_csv(submission_dir / "cohort_retention.csv", index=False)

    return retention
