import subprocess

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


response = ask_openclaw("Responde solamente OK")

print("RESPUESTA LIMPIA:")
print(response)