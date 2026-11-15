from pathlib import Path

import numpy as np
import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """

    activity_dir = Path(__file__).resolve().parents[1]
    data_dir = activity_dir / "data"
    submission_dir = activity_dir / "submission"

    channel_data = []
    for channel, filename in [
        ("letter", "historical_requests_letter.csv.gz"),
        ("web", "historical_requests_web.csv.gz"),
    ]:
        requests = pd.read_csv(data_dir / filename, compression="gzip")
        requests = requests.drop_duplicates().copy()
        requests["channel"] = channel
        channel_data.append(requests)

    requests = pd.concat(channel_data, ignore_index=True)
    requests["in_date"] = pd.to_datetime(requests["in_date"])
    requests["out_date"] = pd.to_datetime(requests["out_date"])
    requests["year"] = requests["in_date"].dt.year
    requests["business_days"] = np.nan

    answered = requests["out_date"].notna()
    start_dates = requests.loc[answered, "in_date"].to_numpy(dtype="datetime64[D]")
    end_dates = requests.loc[answered, "out_date"].to_numpy(dtype="datetime64[D]")
    requests.loc[answered, "business_days"] = np.busday_count(
        start_dates + np.timedelta64(1, "D"),
        end_dates + np.timedelta64(1, "D"),
    )
    requests["calendar_days"] = (requests["out_date"] - requests["in_date"]).dt.days
    requests["on_time"] = answered & requests["business_days"].le(15)

    channel_summary = (
        requests.groupby("channel", as_index=False, sort=True)
        .agg(
            requests=("channel", "size"),
            answered=("out_date", "count"),
            median_business_days=("business_days", "median"),
            on_time_rate=("on_time", "mean"),
        )
    )
    channel_summary["pending"] = (
        channel_summary["requests"] - channel_summary["answered"]
    )
    channel_summary = channel_summary[
        [
            "channel",
            "requests",
            "answered",
            "pending",
            "median_business_days",
            "on_time_rate",
        ]
    ]

    yearly_summary = (
        requests.groupby(["year", "channel"], as_index=False, sort=True)
        .agg(
            requests=("channel", "size"),
            pending=("out_date", lambda values: values.isna().sum()),
            on_time_rate=("on_time", "mean"),
        )
    )

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    requests["day_name"] = pd.Categorical(
        requests["day_name"], categories=day_order, ordered=True
    )
    entry_day_summary = (
        requests.groupby("day_name", observed=False, sort=True, as_index=False)
        .agg(
            requests=("day_name", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
    )
    entry_day_summary["day_name"] = entry_day_summary["day_name"].astype(str)

    submission_dir.mkdir(parents=True, exist_ok=True)
    channel_summary.to_csv(submission_dir / "channel_summary.csv", index=False)
    yearly_summary.to_csv(submission_dir / "yearly_summary.csv", index=False)
    entry_day_summary.to_csv(submission_dir / "entry_day_summary.csv", index=False)

    return channel_summary, yearly_summary, entry_day_summary
