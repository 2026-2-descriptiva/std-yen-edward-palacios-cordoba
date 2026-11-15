from .analysis import SUBMISSION_DIRECTORY
from .pregunta_01 import clean_campaign_data


def main():
    tables = clean_campaign_data()
    for name, table in zip(("client", "campaign", "economics"), tables):
        print(
            f"{name}: {len(table)} filas -> "
            f"{SUBMISSION_DIRECTORY / f'{name}.csv'}"
        )
        print(table.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
