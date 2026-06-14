import os


def save_report(
    text,
    output_path
):

    folder = os.path.dirname(output_path)

    if folder:
        os.makedirs(
            folder,
            exist_ok=True
        )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(text)

    return output_path