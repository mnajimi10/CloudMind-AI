from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = ROOT_DIR / "data" / "raw" / "azure_costs.csv"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
QUARANTINE_DIR = ROOT_DIR / "data" / "quarantine"
REPORT_DIR = ROOT_DIR / "reports"

CLEAN_FILE = PROCESSED_DIR / "azure_costs_clean.csv"
REJECTED_FILE = QUARANTINE_DIR / "azure_costs_rejected.csv"
REPORT_FILE = REPORT_DIR / "etl_report.json"

REQUIRED_COLUMNS = [
    "Date",
    "SubscriptionId",
    "ResourceId",
    "ResourceName",
    "ResourceType",
    "ServiceName",
    "MeterName",
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

DUPLICATE_KEY = ["Date", "ResourceId", "MeterName"]