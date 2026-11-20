
import json
from decimal import Decimal
from pathlib import Path

import pandas as pd

from pipeline.db import get_connection


ROOT_DIR = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = ROOT_DIR / "data" / "processed" / "azure_costs_clean.csv"


INSERT_QUERY = """
    INSERT INTO cloud_costs (
        usage_date,
        subscription_id,
        subscription_name,
        resource_group,
        resource_id,
        resource_name,
        resource_type,
        service_name,
        service_family,
        meter_category,
        meter_name,
        region,
        quantity,
        unit_of_measure,
        effective_price,
        cost,
        currency,
        tags
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s,
        CAST(%s AS JSONB)
    )
    ON CONFLICT (usage_date, resource_id, meter_name)
    DO UPDATE SET
        subscription_id = EXCLUDED.subscription_id,
        subscription_name = EXCLUDED.subscription_name,
        resource_group = EXCLUDED.resource_group,
        resource_name = EXCLUDED.resource_name,
        resource_type = EXCLUDED.resource_type,
        service_name = EXCLUDED.service_name,
        service_family = EXCLUDED.service_family,
        meter_category = EXCLUDED.meter_category,
        region = EXCLUDED.region,
        quantity = EXCLUDED.quantity,
        unit_of_measure = EXCLUDED.unit_of_measure,
        effective_price = EXCLUDED.effective_price,
        cost = EXCLUDED.cost,
        currency = EXCLUDED.currency,
        tags = EXCLUDED.tags;
"""


def to_decimal(value):
    """Convert a CSV numeric value into Decimal."""
    return Decimal(str(value))


def prepare_rows(df):
    """Map Azure CSV columns to PostgreSQL columns."""

    rows = []

    for _, row in df.iterrows():

        tags = json.loads(row["Tags"])

        values = (
            pd.to_datetime(row["Date"]).date(),
            str(row["SubscriptionId"]),
            row["SubscriptionName"],
            row["ResourceGroup"],
            row["ResourceId"],
            row["ResourceName"],
            row["ResourceType"],
            row["ServiceName"],
            row["ServiceFamily"],
            row["MeterCategory"],
            row["MeterName"],
            row["Region"],
            to_decimal(row["Quantity"]),
            row["UnitOfMeasure"],
            to_decimal(row["EffectivePrice"]),
            to_decimal(row["CostInBillingCurrency"]),
            row["BillingCurrency"],
            json.dumps(tags),
        )

        rows.append(values)

    return rows


def load_to_postgres():
    """Load clean Azure cost data into PostgreSQL."""

    if not CLEAN_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Clean CSV not found: {CLEAN_DATA_PATH}"
        )

    df = pd.read_csv(CLEAN_DATA_PATH)

    if df.empty:
        print("No data to load.")
        return

    rows = prepare_rows(df)

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.executemany(INSERT_QUERY, rows)
        connection.commit()

        print("PostgreSQL loading successful!")
        print(f"Rows processed: {len(rows)}")

    except Exception:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    load_to_postgres()
