import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime

OPENCLAW = r"C:\Users\jmcas\AppData\Roaming\npm\openclaw.cmd"


def ask_openclaw(prompt):

    result = subprocess.run(
        [
            OPENCLAW,
            "infer",
            "model",
            "run",
            "--local",
            "--prompt",
            prompt
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    output = result.stdout.strip()

    lines = output.splitlines()

    filtered = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line.startswith("model.run"):
            continue

        if line.startswith("provider:"):
            continue

        if line.startswith("model:"):
            continue

        if line.startswith("outputs:"):
            continue

        filtered.append(line)

    return "\n".join(filtered)


def analyze_excel(file_path):

    df = pd.read_excel(file_path)

    summary = {
        "rows": len(df),
        "columns": list(df.columns)
    }

    if "Precio" in df.columns:

        summary["precio_min"] = float(df["Precio"].min())
        summary["precio_max"] = float(df["Precio"].max())
        summary["precio_promedio"] = float(df["Precio"].mean())

    return summary


def build_prompt(summary):

    return (
        f"Analiza los siguientes datos financieros. "
        f"Filas: {summary['rows']}. "
        f"Columnas: {summary['columns']}. "
        f"Precio mínimo: {summary['precio_min']}. "
        f"Precio máximo: {summary['precio_max']}. "
        f"Precio promedio: {summary['precio_promedio']}. "
        f"Genera un resumen breve, una tendencia observada y una conclusión."
    )


if __name__ == "__main__":

    excel_file = "data/excel/sample.xlsx"

    summary = analyze_excel(excel_file)

    prompt = build_prompt(summary)

    print("\n=== PROMPT ===\n")
    print(prompt)

    analysis = ask_openclaw(prompt)

    if not analysis:
        analysis = "ERROR: OpenClaw devolvió una respuesta vacía."

    print("\n=== ANALISIS IA ===\n")
    print(analysis)

    Path("reports").mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_file = f"reports/analysis_report_{timestamp}.txt"

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(analysis)

    print("\nReporte guardado:")
    print(report_file)