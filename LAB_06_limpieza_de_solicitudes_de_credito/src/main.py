from .analysis import OUTPUT_FILE
from .pregunta_01 import pregunta_01


def main():
    data = pregunta_01()
    print(f"Dataset limpio: {len(data)} filas, {len(data.columns)} columnas")
    print(f"Archivo generado: {OUTPUT_FILE}")
    print(data.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
