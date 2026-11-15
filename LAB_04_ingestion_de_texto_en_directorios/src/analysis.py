from pathlib import Path

import pandas as pd


ACTIVITY_DIRECTORY = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = ACTIVITY_DIRECTORY / "data"
SUBMISSION_DIRECTORY = ACTIVITY_DIRECTORY / "submission"
SPLITS = ("train", "test")


def build_datasets():
    datasets = {}
    SUBMISSION_DIRECTORY.mkdir(parents=True, exist_ok=True)

    for split in SPLITS:
        split_directory = DATA_DIRECTORY / split
        records = []

        for target_directory in sorted(
            path for path in split_directory.iterdir() if path.is_dir()
        ):
            target = target_directory.name
            for text_file in sorted(target_directory.glob("*.txt")):
                phrase = text_file.read_text(encoding="utf-8").strip()
                if not phrase:
                    raise ValueError(f"El archivo no contiene una frase: {text_file}")
                records.append({"phrase": phrase, "target": target})

        dataset = pd.DataFrame(records, columns=["phrase", "target"])
        dataset.to_csv(
            SUBMISSION_DIRECTORY / f"{split}_dataset.csv",
            index=False,
            encoding="utf-8",
        )
        datasets[split] = dataset

    return datasets
