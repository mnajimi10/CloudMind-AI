
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

SOURCE_FILE = ROOT_DIR / "data" / "raw" / "azure_costs.csv"
OUTPUT_FILE = ROOT_DIR / "data" / "raw" / "azure_costs_corrupted.csv"

df = pd.read_csv(SOURCE_FILE)

# We need at least 7 rows
if len(df) < 7:
    raise ValueError("Dataset must contain at least 7 rows")

# 1. Invalid date
df.loc[0, "Date"] = "not-a-date"

# 2. Missing resource name
df.loc[1, "ResourceName"] = None

# 3. Negative cost
df.loc[2, "CostInBillingCurrency"] = -50

# 4. Invalid quantity
df.loc[3, "Quantity"] = "abc"

# 5. Duplicate business key
df.loc[4] = df.loc[5].copy()

# 6. Invalid JSON tags
df.loc[6, "Tags"] = "{invalid-json}"

# 7. Inconsistent cost
df.loc[7, "CostInBillingCurrency"] = 9999

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("Corrupted dataset generated!")
print(f"Original rows: {len(pd.read_csv(SOURCE_FILE))}")
print(f"Corrupted rows: {len(df)}")
print(f"Output: {OUTPUT_FILE}")
