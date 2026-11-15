from .analysis import build_cluster_dataframe


def main():
    clusters = build_cluster_dataframe()
    print(f"Clústeres extraídos y normalizados: {len(clusters)}")
    print(
        "Se reconstruyeron las líneas continuadas, se normalizaron los "
        "espacios y se convirtió la coma decimal a punto."
    )
    print(clusters.to_string(index=False))


if __name__ == "__main__":
    main()
