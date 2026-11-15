from .pregunta_01 import build_cohort_analysis


def main() -> None:
    retention = build_cohort_analysis()
    print("Retencion de clientes por cohorte y periodo")
    print(retention.to_string(index=False))
    print("\nArchivos generados en submission/:")
    print("- cohort_retention.csv")
    print("- cohort_retention_heatmap.png")


if __name__ == "__main__":
    main()
