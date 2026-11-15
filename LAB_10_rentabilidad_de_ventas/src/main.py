from .pregunta_01 import pregunta_01


def main() -> None:
    titles = [
        "Resumen de rentabilidad",
        "Rentabilidad por rango de descuento",
        "Segmentos prioritarios por utilidad perdida",
    ]
    for title, table in zip(titles, pregunta_01()):
        print(f"\n{title}")
        print(table.to_string(index=False))


if __name__ == "__main__":
    main()
