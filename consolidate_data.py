"""Consolidate FPS-level raw JSON files into an analysis-ready CSV."""

import json
from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/consolidated.csv")


def clean_number(value):
    """Convert scraped numeric text into a numeric value."""
    if value is None:
        return 0

    value = str(value).strip().replace(",", "")

    if value == "":
        return 0

    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except ValueError:
        return value


def flatten_table(table, prefix):
    """Flatten a table dictionary into descriptive column names."""
    result = {}

    if not isinstance(table, dict):
        return result

    for row_name, values in table.items():
        if not isinstance(values, dict):
            continue

        row_key = (
            str(row_name)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )

        for column_name, value in values.items():
            column_key = (
                str(column_name)
                .strip()
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
            )

            result[f"{prefix}_{row_key}_{column_key}"] = clean_number(value)

    return result


def flatten_record(data):
    """Convert one FPS JSON record into one flat dictionary."""
    record = {
        "year": data.get("year"),
        "month": data.get("month"),
        "state": data.get("state"),
        "district": data.get("district"),
        "fps_id": data.get("fps_id"),
        "fps_name": data.get("fps_name"),
    }

    summary = data.get("summary", data.get("summary_cards", {}))
    for key, value in summary.items():
        column = (
            str(key).strip().lower().replace(" ", "_")
        )
        record[f"summary_{column}"] = clean_number(value)

    record.update(
        flatten_table(
            data.get("transactions", data.get("number_of_transactions", {})),
            "txn",
        )
    )

    record.update(
        flatten_table(
            data.get(
                "ration_cards",
                data.get("number_of_transacted_ration_cards", {}),
            ),
            "ration_card",
        )
    )

    record.update(
        flatten_table(
            data.get(
                "distribution",
                data.get("distributed_quantity_kg", {}),
            ),
            "distribution",
        )
    )

    return record


def main():
    """Load all raw JSON files and write the consolidated CSV."""
    json_files = sorted(RAW_DIR.rglob("*.json"))

    if not json_files:
        print(f"No JSON files found in {RAW_DIR}")
        return

    records = []
    failed_files = []

    for file_path in json_files:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            records.append(flatten_record(data))

        except (OSError, json.JSONDecodeError, TypeError, KeyError) as error:
            failed_files.append((str(file_path), str(error)))
            print(f"Failed: {file_path} -> {error}")

    if not records:
        print("No valid records were found.")
        return

    df = pd.DataFrame(records)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Consolidated {len(df)} FPS records.")
    print(f"Saved to: {OUTPUT_FILE}")

    if failed_files:
        print(f"Files skipped due to errors: {len(failed_files)}")


if __name__ == "__main__":
    main()
