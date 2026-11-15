# Cohortes de clientes

## Propósito

Analizar cómo evoluciona la retención de clientes desde su primera compra y distinguir patrones observados de períodos aún no observables.

## Competencia

Construye cohortes temporales, calcula tasas de retención con su denominador correcto y comunica la matriz resultante mediante un mapa de calor en Matplotlib.

## Datos

`data/sales.csv.gz` contiene órdenes de compra de clientes entre enero y agosto de 2022.

## Restricciones

Genere `cohort_retention.csv` y `cohort_retention_heatmap.png` en `submission/`. No convierta períodos no observados en retención cero.

## Ejecución

Desde la raíz del repositorio, genere los archivos e imprima la tabla de
retención con:

```powershell
python -m LAB_12_cohortes_de_clientes.src.main
```

Para ejecutar la prueba:

```powershell
python -m pytest LAB_12_cohortes_de_clientes/tests/test_activity.py -q
```
