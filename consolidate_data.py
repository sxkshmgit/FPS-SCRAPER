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


def clean_key(value):
    """Create consistent column-name fragments from scraped labels."""
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
    )


def flatten_summary(summary):
    """Flatten summary-card values into descriptive columns."""
    result = {}

    if not isinstance(summary, dict):
        return result

    for key, value in summary.items():
        result[f"summary_{clean_key(key)}"] = clean_number(value)

    return result


def flatten_table(table, prefix):
    """Flatten either a list-based or dictionary-based table."""
    result = {}

    if isinstance(table, list):
        for row in table:
            if not isinstance(row, dict):
                continue

            row_name = row.get("row_label")
            if not row_name or clean_key(row_name) == "total":
                continue

            row_key = clean_key(row_name)

            for column_name, value in row.items():
                if column_name == "row_label":
                    continue

                result[f"{prefix}_{row_key}_{clean_key(column_name)}"] = clean_number(value)

    elif isinstance(table, dict):
        for row_name, values in table.items():
            if not isinstance(values, dict) or clean_key(row_name) == "total":
                continue

            row_key = clean_key(row_name)

            for column_name, value in values.items():
                result[f"{prefix}_{row_key}_{clean_key(column_name)}"] = clean_number(value)

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

    summary = data.get("summary_cards", data.get("summary", {}))
    record.update(flatten_summary(summary))

    transactions = data.get(
        "number_of_transactions",
        data.get("transactions", []),
    )
    record.update(flatten_table(transactions, "txn"))

    ration_cards = data.get(
        "number_of_transacted_ration_cards",
        data.get("ration_cards", []),
    )
    record.update(flatten_table(ration_cards, "ration_card"))

    distribution = data.get(
        "distributed_quantity_kg",
        data.get("distribution", []),
    )
    record.update(flatten_table(distribution, "distribution"))

    # Add basic data-quality flags required for identifying incomplete records.
    record["has_transactions_data"] = bool(transactions)
    record["has_ration_cards_data"] = bool(ration_cards)
    record["has_distribution_data"] = bool(distribution)

    total_transaction = record.get("txn_priority_household_phh_total", 0)
    total_transaction += record.get("txn_antyodaya_anna_yojana_aay_total", 0)
    record["no_transactions"] = total_transaction == 0

    return record


def main():
    """Load all raw JSON files and write the consolidated CSV."""
    json_files = sorted(RAW_DIR.rglob("*.json"))

    if not json_files:
        print(f"No JSON files found in {RAW_DIR}")
        return

    records = []
    failed_files = []

    for index, file_path in enumerate(json_files, start=1):
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            records.append(flatten_record(data))

        except (OSError, json.JSONDecodeError, TypeError, KeyError) as error:
            failed_files.append((str(file_path), str(error)))
            print(f"Failed [{index}/{len(json_files)}]: {file_path} -> {error}")

    if not records:
        print("No valid records were found.")
        return

    df = pd.DataFrame(records)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Consolidated {len(df)} FPS records.")
    print(f"Columns created: {len(df.columns)}")
    print(f"Saved to: {OUTPUT_FILE}")

    if failed_files:
        print(f"Files skipped due to errors: {len(failed_files)}")
    else:
        print("All raw JSON files were processed successfully.")


if __name__ == "__main__":
    main()
