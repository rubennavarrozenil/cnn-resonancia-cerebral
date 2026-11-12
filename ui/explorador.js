export default function render({ data, parentElement }) {
  const find = (id) => parentElement.getElementById(id);
  find("test-count").textContent = data.total;
  find("comparison-count").textContent = data.total;
  find("correct").textContent = data.correct;
  find("accuracy").textContent = data.accuracy;
  find("baseline-accuracy").textContent = data.baselineAccuracy;
  find("macro-f1").textContent = data.macroF1;
  find("report-link").href = data.reportUrl;
  find("repository-link").href = data.repositoryUrl;

  const classColumns = find("class-columns");
  const rows = find("matrix-body");
  while (classColumns.cells.length > 1) classColumns.deleteCell(1);
  rows.replaceChildren();

  function classHeader(label, scope) {
    const header = document.createElement("th");
    header.scope = scope;
    const breakAt = { Meningioma: 5, Hipofisario: 6 }[label];
    if (breakAt) {
      header.append(label.slice(0, breakAt), document.createElement("wbr"), label.slice(breakAt));
    } else {
      header.textContent = label;
    }
    return header;
  }

  for (const label of data.classes) {
    classColumns.append(classHeader(label, "col"));
  }

  const cells = data.classes.map((real, rowIndex) => {
    const row = rows.insertRow();
    row.append(classHeader(real, "row"));

    return data.classes.map((_, columnIndex) => {
      const count = data.counts[rowIndex][columnIndex];
      const button = document.createElement("button");
      button.type = "button";
      button.className = "cell";
      button.dataset.row = rowIndex;
      button.dataset.column = columnIndex;
      button.dataset.intensity = count === 0 ? "zero" : count >= 100 ? "high" : count >= 10 ? "medium" : "low";
      button.setAttribute("aria-pressed", "false");
      row.insertCell().append(button);
      return button;
    });
  });

  const matrixView = find("matrix-view");
  const percentOption = find("percentages-view");
  find("counts-view").checked = true;

  function updateView() {
    const showPercent = percentOption.checked;
    const mode = showPercent ? "percentages" : "counts";
    for (const [rowIndex, row] of cells.entries()) {
      for (const [columnIndex, button] of row.entries()) {
        const count = data.counts[rowIndex][columnIndex];
        const real = data.classes[rowIndex];
        const predicted = data.classes[columnIndex];
        const value = data[mode][rowIndex][columnIndex];
        const unit = count === 1 ? "corte" : "cortes";
        const measurement = showPercent ? `${value} dentro de la clase real` : `${value} ${unit}`;
        button.textContent = value;
        button.dataset.view = mode;
        button.setAttribute("aria-label", `Etiqueta del conjunto de datos ${real}. Predicción del modelo ${predicted}. ${measurement}.`);
      }
    }
  }
  updateView();

  const detail = find("selection-detail");
  const detailTitle = find("detail-title");
  const detailCard = find("detail-card");
  const empty = find("empty-detail");
  const announcement = find("announcement");
  const findings = find("findings");
  let selectedButton;
  detail.hidden = true;
  empty.hidden = false;
  announcement.textContent = "";

  function selectCell(row, column) {
    const button = cells[row][column];
    if (button === selectedButton) return;
    selectedButton?.setAttribute("aria-pressed", "false");
    button.setAttribute("aria-pressed", "true");
    selectedButton = button;

    const real = data.classes[row];
    const predicted = data.classes[column];
    const count = data.counts[row][column];
    const support = data.supports[row];
    const percentage = data.percentages[row][column];
    const kind = count === 0 ? "Sin casos" : row === column ? "Acierto" : "Error";
    const result = `${count} de ${support} (${percentage})`;
    find("selection-kind").textContent = kind;
    find("real-class").textContent = real;
    find("predicted-class").textContent = predicted;
    find("selection-count").textContent = result;
    find("interpretation").textContent = `De los ${support} cortes etiquetados como «${real}», ${count} recibieron la predicción «${predicted}».`;
    detail.hidden = false;
    empty.hidden = true;
    announcement.textContent = `${kind}. Etiqueta del conjunto de datos ${real}. Predicción del modelo ${predicted}. ${result}.`;
  }

  function selectFromMatrix(event) {
    const button = event.target.closest("button.cell");
    if (button) selectCell(Number(button.dataset.row), Number(button.dataset.column));
  }

  function selectFinding(event) {
    const button = event.target.closest("button[data-row]");
    if (!button) return;
    selectCell(Number(button.dataset.row), Number(button.dataset.column));
    detailTitle.focus({ preventScroll: true });
    detailCard.scrollIntoView({ block: "nearest", inline: "nearest" });
  }

  rows.addEventListener("click", selectFromMatrix);
  findings.addEventListener("click", selectFinding);
  matrixView.addEventListener("change", updateView);
  return () => {
    rows.removeEventListener("click", selectFromMatrix);
    findings.removeEventListener("click", selectFinding);
    matrixView.removeEventListener("change", updateView);
  };
}
