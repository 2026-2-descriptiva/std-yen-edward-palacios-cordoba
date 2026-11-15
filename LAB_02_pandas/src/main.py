from .analysis import analyze_tables, load_tables


def main():
    tables = load_tables()
    results = analyze_tables(tables)
    print(
        "Tablas cargadas: "
        + ", ".join(f"{name}={len(table)} filas" for name, table in tables.items())
    )
    print(
        "Preparación: espacios externos normalizados, columnas numéricas "
        "validadas y fechas conservadas como texto para extraer el año."
    )
    print(
        "Valores faltantes detectados: "
        f"{sum(int(table.isna().sum().sum()) for table in tables.values())}"
    )
    for number, result in results.items():
        print(f"\npregunta_{number}:\n{result}")


if __name__ == "__main__":
    main()
