from .pregunta_01 import pregunta_01


def main() -> None:
    hourly, carriers = pregunta_01()
    print("\nTasas nacionales de demora por hora")
    print(hourly.to_string(index=False))
    print("\nRanking de aerolíneas: tasa observada vs. ajustada por horario")
    print(carriers.to_string(index=False))


if __name__ == "__main__":
    main()
