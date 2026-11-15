import json

import pandas as pd

from .analysis import PUBLISHED_FILE, REPORT_FILE
from .pregunta_01 import pregunta_01


def main():
    report = pregunta_01()
    published = pd.read_csv(PUBLISHED_FILE)
    print(f"Reporte de privacidad: {REPORT_FILE}")
    print(f"Esquema elegido: {report['selected_scheme']}")
    print(f"Registros publicados: {len(published)}")
    print(published.head(5).to_string(index=False))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
