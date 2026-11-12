"""Explorador en Streamlit de una corrida académica guardada."""

import logging
from pathlib import Path

import streamlit as st

from evaluacion import CLASS_LABELS, CLASS_ORDER, EvaluationDataError, cell_percentages, load_matrix, summarize

APP_TITLE = "Clasificación de cortes de resonancia cerebral"
UI = Path(__file__).resolve().parent / "ui"
REPOSITORY_URL = "https://github.com/rubennavarrozenil/cnn-resonancia-cerebral"
REPORT_URL = f"{REPOSITORY_URL}/blob/main/docs/informe.pdf"
LOGGER = logging.getLogger(__name__)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    try:
        matrix = load_matrix()
    except EvaluationDataError as error:
        LOGGER.warning("Evaluación no disponible (%s).", error)
        st.title(APP_TITLE)
        st.error("Los resultados de la evaluación no están disponibles. Vuelve a intentarlo más tarde.")
        st.stop()

    metrics = summarize(matrix)
    percentages = cell_percentages(matrix)
    supports = tuple(map(sum, matrix))
    baseline_correct = supports[CLASS_ORDER.index("pituitary")]
    st.html(UI / "streamlit.css")
    render = st.components.v2.component(
        "cnn_evaluation",
        html=(UI / "explorador.html").read_text(encoding="utf-8"),
        css=(UI / "explorador.css").read_text(encoding="utf-8"),
        js=(UI / "explorador.js").read_text(encoding="utf-8"),
    )
    render(
        key="cnn_evaluation",
        data={
            "classes": CLASS_LABELS,
            "counts": matrix,
            "supports": supports,
            "percentages": [[f"{value:.2f} %" for value in row] for row in percentages],
            "total": metrics.total,
            "correct": f"{metrics.correct} de {metrics.total}",
            "accuracy": f"{100 * metrics.accuracy:.2f} %",
            "baselineAccuracy": f"{100 * baseline_correct / metrics.total:.2f} %",
            "macroF1": f"{metrics.macro_f1:.4f}",
            "reportUrl": REPORT_URL,
            "repositoryUrl": REPOSITORY_URL,
        },
    )


if __name__ == "__main__":
    main()
