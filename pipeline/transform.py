import json
import pandas as pd

from pipeline.config import NUMERIC_COLUMNS


def transform_data(df):
    df = df.copy()

    # Normalize dates
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Convert numeric fields
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Normalize text fields
    text_columns = [
        "SubscriptionId",
        "ResourceId",
        "ResourceName",
        "ServiceName",
        "BillingCurrency",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    # Parse tags into Python dictionaries
    def parse_tags(value):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else None
        except (TypeError, ValueError):
            return None

    df["ParsedTags"] = df["Tags"].apply(parse_tags)

    print("[TRANSFORM] Data types normalized")

    return df