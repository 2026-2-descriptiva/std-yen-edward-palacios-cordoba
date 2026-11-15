# Limpieza de campañas

## Propósito

Transformar registros crudos de una campaña bancaria en tablas analíticas de clientes, contactos y contexto económico.

## Competencia

Integra archivos comprimidos, limpia variables categóricas y construye una fecha a partir de atributos separados para producir datos tabulares reutilizables.

## Datos

Los diez archivos comprimidos de `data/` contienen los registros originales de la campaña.

## Restricciones

Procese los archivos directamente comprimidos y conserve las tres salidas solicitadas como CSV en `submission/`.

## Ejecución

Desde la raíz del repositorio, genere las tres tablas y vea una muestra:

```bash
python -m LAB_07_limpieza_de_campanas.src.main
```

Para validar la solución:

```bash
python -m pytest LAB_07_limpieza_de_campanas/tests/test_activity.py -q
```
