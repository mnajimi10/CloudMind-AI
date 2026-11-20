import pandas as pd

from pipeline.config import RAW_FILE, REQUIRED_COLUMNS


def extract_data():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {RAW_FILE}"
        )

    df = pd.read_csv(RAW_FILE)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Preserve source row number for traceability
    df["_source_row"] = range(2, len(df) + 2)

    print(f"[EXTRACT] {len(df)} rows extracted")

    return df