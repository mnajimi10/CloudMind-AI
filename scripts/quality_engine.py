
import json
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT_DIR / "data" / "raw" / "azure_costs.csv"
# INPUT_FILE = ROOT_DIR / "data" / "raw" / "azure_costs_corrupted.csv"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
QUARANTINE_DIR = ROOT_DIR / "data" / "quarantine"
REPORT_DIR = ROOT_DIR / "reports"

PROCESSED_FILE = PROCESSED_DIR / "azure_costs_clean.csv"
REJECTED_FILE = QUARANTINE_DIR / "azure_costs_rejected.csv"
REPORT_FILE = REPORT_DIR / "data_quality_report.json"

REQUIRED_COLUMNS = [
    "Date",
    "SubscriptionId",
    "ResourceId",
    "ResourceName",
    "ServiceName",
    "Quantity",
    "EffectivePrice",
    "CostInBillingCurrency",
    "BillingCurrency",
    "Tags",
]

NUMERIC_COLUMNS = [
    "Quantity",
    "EffectivePrice",
    "CostInBillingCurrency",
]

KEY_COLUMNS = [
    "Date",
    "ResourceId",
    "MeterName",
]

# --------------------------------------------------
# INITIALIZATION
# --------------------------------------------------

for directory in [PROCESSED_DIR, QUARANTINE_DIR, REPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# Preserve original data
df["_source_row"] = range(2, len(df) + 2)

issues = []
reasons = pd.Series("", index=df.index, dtype="object")

def add_issue(rule, count, description):
    issues.append({
        "rule": rule,
        "failed_rows": int(count),
        "description": description,
    })

def reject(mask, reason):
    mask = mask.fillna(True)
    reasons.loc[mask] = reasons.loc[mask].apply(
        lambda current: (
            f"{current}; {reason}" if current else reason
        )
    )

# --------------------------------------------------
# DQ001 - SCHEMA VALIDATION
# --------------------------------------------------

missing_columns = [
    col for col in REQUIRED_COLUMNS if col not in df.columns
]

add_issue(
    "DQ001",
    len(missing_columns),
    f"Missing columns: {missing_columns}"
)

if missing_columns:
    raise ValueError(
        f"CSV schema invalid. Missing columns: {missing_columns}"
    )

# --------------------------------------------------
# DQ002 - REQUIRED FIELDS
# --------------------------------------------------

required_fields = [
    "Date",
    "SubscriptionId",
    "ResourceId",
    "ResourceName",
    "ServiceName",
    "BillingCurrency",
    "Tags",
]

missing_mask = pd.Series(False, index=df.index)

for col in required_fields:
    missing_mask |= (
        df[col].isna()
        | df[col].astype(str).str.strip().eq("")
    )

add_issue(
    "DQ002",
    missing_mask.sum(),
    "Missing required values"
)

reject(missing_mask, "Missing required values")

# --------------------------------------------------
# DQ003 - DATE VALIDATION
# --------------------------------------------------

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

invalid_dates = df["Date"].isna()

add_issue(
    "DQ003",
    invalid_dates.sum(),
    "Invalid or missing dates"
)

reject(invalid_dates, "Invalid date")

# --------------------------------------------------
# DQ004 - NUMERIC VALIDATION
# --------------------------------------------------

invalid_numeric = pd.Series(False, index=df.index)

for col in NUMERIC_COLUMNS:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    invalid_numeric |= (
        df[col].isna()
        | ~df[col].map(
            lambda value: (
                pd.notna(value)
                and abs(value) != float("inf")
            )
        )
    )

add_issue(
    "DQ004",
    invalid_numeric.sum(),
    "Invalid numeric values"
)

reject(invalid_numeric, "Invalid numeric value")

# --------------------------------------------------
# DQ005 - NEGATIVE VALUES
# --------------------------------------------------

negative_mask = (
    (df["Quantity"] < 0)
    | (df["EffectivePrice"] < 0)
    | (df["CostInBillingCurrency"] < 0)
)

negative_mask = negative_mask.fillna(False)

add_issue(
    "DQ005",
    negative_mask.sum(),
    "Negative quantity, price or cost"
)

reject(negative_mask, "Negative numeric value")

# --------------------------------------------------
# DQ006 - DUPLICATE BUSINESS KEYS
# --------------------------------------------------

duplicate_mask = df.duplicated(
    subset=KEY_COLUMNS,
    keep="first"
)

add_issue(
    "DQ006",
    duplicate_mask.sum(),
    "Duplicate business keys"
)

reject(duplicate_mask, "Duplicate business key")

# --------------------------------------------------
# DQ007 - TAGS VALIDATION
# --------------------------------------------------

def valid_tags(value):
    try:
        parsed = json.loads(value)
        return isinstance(parsed, dict)
    except (TypeError, ValueError):
        return False

invalid_tags = ~df["Tags"].apply(valid_tags)

add_issue(
    "DQ007",
    invalid_tags.sum(),
    "Invalid JSON tags"
)

reject(invalid_tags, "Invalid JSON tags")

# --------------------------------------------------
# DQ008 - COST CONSISTENCY
# --------------------------------------------------

expected_cost = (
    df["Quantity"] * df["EffectivePrice"]
).round(2)

cost_difference = (
    df["CostInBillingCurrency"] - expected_cost
).abs()

inconsistent_cost = (
    cost_difference > 0.01
).fillna(False)

add_issue(
    "DQ008",
    inconsistent_cost.sum(),
    "Cost does not match quantity multiplied by price"
)

reject(inconsistent_cost, "Inconsistent cost calculation")

# --------------------------------------------------
# FINAL CLASSIFICATION
# --------------------------------------------------

rejected_mask = reasons.ne("")

valid_df = df.loc[~rejected_mask].copy()
rejected_df = df.loc[rejected_mask].copy()

rejected_df["RejectionReason"] = reasons.loc[rejected_mask]

# Restore date format for CSV
valid_df["Date"] = valid_df["Date"].dt.strftime("%Y-%m-%d")
rejected_df["Date"] = rejected_df["Date"].apply(
    lambda value: value.strftime("%Y-%m-%d")
    if pd.notna(value) else ""
)

valid_df = valid_df.drop(columns=["_source_row"])
rejected_df = rejected_df.drop(columns=["_source_row"])

# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

valid_df.to_csv(
    PROCESSED_FILE,
    index=False,
    encoding="utf-8-sig"
)

rejected_df.to_csv(
    REJECTED_FILE,
    index=False,
    encoding="utf-8-sig"
)

# --------------------------------------------------
# QUALITY REPORT
# --------------------------------------------------

report = {
    "source_file": str(INPUT_FILE.name),
    "total_rows": int(len(df)),
    "valid_rows": int(len(valid_df)),
    "rejected_rows": int(len(rejected_df)),
    "quality_percentage": round(
        len(valid_df) / len(df) * 100, 2
    ) if len(df) else 0,
    "rules": issues,
}

REPORT_FILE.write_text(
    json.dumps(report, indent=4, ensure_ascii=False),
    encoding="utf-8"
)

print("=" * 55)
print("CLOUDMIND AI - DATA QUALITY REPORT")
print("=" * 55)

print(f"Total rows: {len(df)}")
print(f"Valid rows: {len(valid_df)}")
print(f"Rejected rows: {len(rejected_df)}")

print(f"Quality score: {report['quality_percentage']}%")

print("\nRule results:")

for issue in issues:
    print(
        f"{issue['rule']}: "
        f"{issue['failed_rows']} failed rows"
    )

print("\nGenerated files:")
print(PROCESSED_FILE)
print(REJECTED_FILE)
print(REPORT_FILE)
