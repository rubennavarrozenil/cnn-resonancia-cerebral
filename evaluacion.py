"""Contrato y cálculos de la evaluación agregada."""

import json
from dataclasses import dataclass
from pathlib import Path

CLASS_ORDER = ("glioma", "healthy", "meningioma", "pituitary")
CLASS_LABELS = ("Glioma", "Sin tumor", "Meningioma", "Hipofisario")
EXPECTED_SUPPORTS = (243, 255, 231, 261)
EXPECTED_RUN = {"seed": 42, "epoch": 15, "split": "test", "test_count": 990}
DATA_PATH = Path(__file__).resolve().parent / "data" / "evaluacion.json"

Matrix = tuple[tuple[int, ...], ...]


class EvaluationDataError(ValueError):
    """El recurso local no cumple el contrato de esta corrida."""


@dataclass(frozen=True)
class Metrics:
    correct: int
    total: int
    accuracy: float
    macro_f1: float


def load_matrix(path: Path = DATA_PATH) -> Matrix:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise EvaluationDataError("recurso ausente") from error
    except OSError as error:
        raise EvaluationDataError("recurso inaccesible") from error
    except (ValueError, RecursionError) as error:
        raise EvaluationDataError("JSON ilegible") from error

    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise EvaluationDataError("versión de esquema inválida")
    dataset = payload.get("dataset")
    if dataset != {
        "name": "Brain Tumor (MRI Scans)",
        "slug": "rm1000/brain-tumor-mri-scans",
        "version": 1,
    } or payload.get("run") != EXPECTED_RUN:
        raise EvaluationDataError("metadatos de la corrida inválidos")
    if payload.get("class_order") != list(CLASS_ORDER):
        raise EvaluationDataError("orden de clases inválido")

    rows = payload.get("matrix")
    size = len(CLASS_ORDER)
    if not isinstance(rows, list) or len(rows) != size or any(
        not isinstance(row, list) or len(row) != size for row in rows
    ):
        raise EvaluationDataError("dimensiones de matriz inválidas")
    if any(type(count) is not int or count < 0 for row in rows for count in row):
        raise EvaluationDataError("conteos de matriz inválidos")

    supports = tuple(map(sum, rows))
    if sum(supports) != EXPECTED_RUN["test_count"]:
        raise EvaluationDataError("total de prueba inválido")
    if supports != EXPECTED_SUPPORTS:
        raise EvaluationDataError("soportes de clase inválidos")
    return tuple(tuple(row) for row in rows)


def summarize(matrix: Matrix) -> Metrics:
    supports = tuple(map(sum, matrix))
    predicted = tuple(map(sum, zip(*matrix, strict=True)))
    diagonal = tuple(row[index] for index, row in enumerate(matrix))
    correct = sum(diagonal)
    total = sum(supports)
    class_f1 = [
        2 * hits / (support + predictions)
        for hits, support, predictions in zip(diagonal, supports, predicted, strict=True)
    ]
    return Metrics(correct, total, correct / total, sum(class_f1) / len(class_f1))


def cell_percentages(matrix: Matrix) -> tuple[tuple[float, ...], ...]:
    return tuple(
        tuple(100 * count / support for count in row)
        for row, support in zip(matrix, map(sum, matrix), strict=True)
    )
