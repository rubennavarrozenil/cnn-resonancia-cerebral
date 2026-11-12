# Clasificación de cortes de resonancia cerebral

Entrenamos una red neuronal convolucional (CNN) para clasificar cortes 2D de resonancia magnética cerebral en cuatro categorías. La demo permite explorar los aciertos y los errores de la CNN en los **990 cortes reservados para prueba**. Por ejemplo, **9 de los 231 cortes etiquetados como meningioma** recibieron la predicción «Sin tumor» (3.90 %).

[Explorar la demo en Streamlit](https://cnn-resonancia-cerebral.streamlit.app/) · [Leer el informe completo](docs/informe.pdf)

## Autoría

Angie Stefany Vera Medina, Gabriel Eduardo Moreno Veloza y Rubén Navarro Zenil realizaron el experimento en equipo.

## Metodología

1. **Datos y partición.** Usamos [Brain Tumor (MRI Scans)][dataset] de Kaggle, versión 1. De 7,023 cortes retiramos 426 copias exactas por MD5 y conservamos 6,597. Agrupamos los cortes que compartían huella visual aHash antes de dividirlos con semilla 42 en entrenamiento, validación y prueba (4,619 / 988 / 990).
2. **CNN.** Convertimos los cortes a RGB de 128 × 128 y los normalizamos con estadísticas de entrenamiento. Aplicamos aumentos de datos durante el entrenamiento. La CNN de PyTorch usa tres bloques convolucionales con 32, 64 y 128 filtros, una capa densa de 256 unidades y Dropout de 0.5. Entrenamos 15 épocas con entropía cruzada, Adam a 0.001 y lotes de 32.
3. **Evaluación.** Evaluamos la época 15 en la partición reservada. Usamos como referencia una regla que predice siempre hipofisario, la clase más frecuente en entrenamiento. Ambos métodos se evaluaron sobre los mismos 990 cortes de prueba.

## Resultados

| Modelo | Aciertos | Exactitud | F1 macro |
|---|---:|---:|---:|
| CNN · época 15 | 941 de 990 | 95.05 % | 0.9492 |
| Regla de referencia · Hipofisario | 261 de 990 | 26.36 % | 0.1043 |

F1 macro promedia el F1 de las cuatro categorías con el mismo peso. En la matriz, las filas son etiquetas del conjunto de datos y las columnas son predicciones. El porcentaje de cada celda usa el total de cortes de su fila. Los [conteos agregados y su procedencia](data/evaluacion.json) alimentan la demo.

Los resultados describen una corrida académica sobre cortes 2D. La independencia por paciente, la validación externa y la utilidad clínica quedan por verificar.

## Ejecutar la demo

Usa **Python 3.12**. Ejecuta los comandos desde la raíz y abre la dirección local que imprime Streamlit.

**PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip==26.3
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

**Bash**

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip==26.3
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run streamlit_app.py
```

[dataset]: https://www.kaggle.com/datasets/rm1000/brain-tumor-mri-scans
