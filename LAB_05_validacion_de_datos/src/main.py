import json

from .analysis import REPORT_FILE
from .pregunta_01 import main as generate_report


def main():
    report = generate_report()
    print(f"Reporte de calidad escrito en: {REPORT_FILE}")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
