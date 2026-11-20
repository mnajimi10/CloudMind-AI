import pandas as pd

from pipeline.config import DUPLICATE_KEY


def validate_data(df):
    df = df.copy()

    # Each row can accumulate multiple rejection reasons
    reasons = pd.Series("", index=df.index, dtype="object")
    report = []

    def reject(mask, message):
        mask = mask.fillna(True)
        reasons.loc[mask] = reasons.loc[mask].apply(
            lambda current: (
                f"{current}; {message}"
                if current else message
            )
        )

    def add_rule(rule, mask, description):
        mask = mask.fillna(False)
        report.append({
            "rule": rule,
            "failed_rows": int(mask.sum()),
            "description": description,
        })

    # DQ001 - Required fields
    required = [
        "Date",
        "SubscriptionId",
        "ResourceId",
        "ResourceName",
        "ServiceName",
        "BillingCurrency",
        "Tags",
    ]

    missing = pd.Series(False, index=df.index)

    for column in required:
        missing |= (
            df[column].isna()
            | df[column].astype("string").str.strip().eq("").fillna(True)
        )

    add_rule("DQ001", missing, "Missing required fields")
    reject(missing, "Missing required fields")

    # DQ002 - Valid dates
    invalid_dates = df["Date"].isna()

    add_rule("DQ002", invalid_dates, "Invalid dates")
    reject(invalid_dates, "Invalid date")

    # DQ003 - Numeric fields
    numeric_columns = [
        "Quantity",
        "EffectivePrice",
        "CostInBillingCurrency",
    ]

    invalid_numeric = pd.Series(False, index=df.index)

    for column in numeric_columns:
        invalid_numeric |= (
            df[column].isna()
            | ~df[column].map(
                lambda value: (
                    pd.notna(value)
                    and abs(value) != float("inf")
                )
            )
        )

    add_rule("DQ003", invalid_numeric, "Invalid numeric values")
    reject(invalid_numeric, "Invalid numeric value")

    # DQ004 - Negative values
    negative = (
        (df["Quantity"] < 0)
        | (df["EffectivePrice"] < 0)
        | (df["CostInBillingCurrency"] < 0)
    ).fillna(False)

    add_rule("DQ004", negative, "Negative values")
    reject(negative, "Negative quantity, price or cost")

    # DQ005 - Duplicate business keys
    duplicate = df.duplicated(
        subset=DUPLICATE_KEY,
        keep="first"
    )

    add_rule("DQ005", duplicate, "Duplicate business keys")
    reject(duplicate, "Duplicate business key")

    # DQ006 - Valid JSON tags
    invalid_tags = df["ParsedTags"].isna()

    add_rule("DQ006", invalid_tags, "Invalid JSON tags")
    reject(invalid_tags, "Invalid JSON tags")

    # DQ007 - Cost calculation
    expected_cost = (
        df["Quantity"] * df["EffectivePrice"]
    ).round(2)

    inconsistent_cost = (
        (df["CostInBillingCurrency"] - expected_cost).abs() > 0.01
    ).fillna(False)

    add_rule("DQ007", inconsistent_cost, "Inconsistent cost")
    reject(inconsistent_cost, "Cost calculation mismatch")

    # Split valid and rejected records
    rejected_mask = reasons.ne("")

    valid_df = df.loc[~rejected_mask].copy()
    rejected_df = df.loc[rejected_mask].copy()

    rejected_df["RejectionReason"] = reasons.loc[rejected_mask]

    print(
        f"[VALIDATE] {len(valid_df)} valid, "
        f"{len(rejected_df)} rejected"
    )

    return valid_df, rejected_df, report