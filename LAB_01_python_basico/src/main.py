from ._data import load_clean_data
from .analysis import analyze_records


def main():
    records = load_clean_data()
    results = analyze_records(records)
    print(f"Registros procesados: {len(records)}")
    invalid_dates = [
        record["date_text"] for record in records if not record["date_is_valid"]
    ]
    print("Preparación: campos recortados, números convertidos,")
    print("y códigos y métricas normalizados y separados.")
    if invalid_dates:
        print(
            f"Fechas de calendario inválidas detectadas ({len(invalid_dates)}); "
            f"se conserva su texto y se usa el mes indicado: {invalid_dates}"
        )
    else:
        print("No se encontraron fechas de calendario inválidas.")
    for number, result in results.items():
        print(f"pregunta_{number}: {result}")


if __name__ == "__main__":
    main()
