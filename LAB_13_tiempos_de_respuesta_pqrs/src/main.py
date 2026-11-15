from .pregunta_01 import pregunta_01


def main() -> None:
    titles = [
        "Resumen por canal",
        "Resumen por año y canal",
        "Tiempos de respuesta por día de entrada",
    ]
    for title, table in zip(titles, pregunta_01()):
        print(f"\n{title}")
        print(table.to_string(index=False))


if __name__ == "__main__":
    main()
