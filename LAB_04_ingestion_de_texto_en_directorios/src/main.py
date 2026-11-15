from .analysis import SUBMISSION_DIRECTORY, build_datasets


def main():
    datasets = build_datasets()
    for split, dataset in datasets.items():
        output_file = SUBMISSION_DIRECTORY / f"{split}_dataset.csv"
        print(f"{split}: {len(dataset)} frases -> {output_file}")
        print(dataset.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
