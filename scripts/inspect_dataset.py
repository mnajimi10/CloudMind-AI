import pandas as pd
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT_DIR / "data" / "raw" / "azure_costs.csv"


df = pd.read_csv(DATA_FILE)

print("=" * 60)
print("CLOUDMIND AI - DATASET INSPECTION")
print("=" * 60)


print("\n[1] DATASET OVERVIEW")

print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")

print("\nColumn names:")
print(df.columns.tolist())


print("\n[2] DATA TYPES")

print(df.dtypes)


print("\n[3] MISSING VALUES")

missing_values = df.isnull().sum()

print(missing_values[missing_values > 0])

if missing_values.sum() == 0:
    print("No missing values detected.")


print("\n[4] DUPLICATES")

duplicate_count = df.duplicated().sum()

print(f"Full-row duplicates: {duplicate_count}")


print("\n[5] DATE ANALYSIS")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

print(f"Minimum date: {df['Date'].min()}")
print(f"Maximum date: {df['Date'].max()}")
print(f"Invalid dates: {df['Date'].isna().sum()}")

print(f"Unique dates: {df['Date'].nunique()}")


print("\n[6] NUMERIC VALIDATION")

numeric_columns = [
    "Quantity",
    "EffectivePrice",
    "CostInBillingCurrency",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

    print(f"\n{column}")
    print(f"  Invalid values: {df[column].isna().sum()}")
    print(f"  Min: {df[column].min()}")
    print(f"  Max: {df[column].max()}")
    print(f"  Mean: {df[column].mean():.2f}")

negative_costs = df[df["CostInBillingCurrency"] < 0]

print(f"\nNegative costs: {len(negative_costs)}")


print("\n[7] COST ANALYSIS")

total_cost = df["CostInBillingCurrency"].sum()

print(f"Total cloud cost: {total_cost:.2f} EUR")

print("\nCost by service:")

cost_by_service = (
    df.groupby("ServiceName")["CostInBillingCurrency"]
    .sum()
    .sort_values(ascending=False)
)

print(cost_by_service.round(2))


print("\n[8] COST BY ENVIRONMENT")

df["Environment"] = df["Tags"].apply(
    lambda tags: __import__("json").loads(tags).get("environment", "unknown")
)

cost_by_environment = (
    df.groupby("Environment")["CostInBillingCurrency"]
    .sum()
    .sort_values(ascending=False)
)

print(cost_by_environment.round(2))


print("\n[9] MONTHLY COST")

df["Month"] = df["Date"].dt.to_period("M")

monthly_cost = (
    df.groupby("Month")["CostInBillingCurrency"]
    .sum()
    .sort_index()
)

print(monthly_cost.round(2))



print("\n[10] TOP 10 EXPENSIVE RESOURCES")

top_resources = (
    df.groupby("ResourceName")["CostInBillingCurrency"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print(top_resources.round(2))



print("\n" + "=" * 60)
print("DATASET INSPECTION COMPLETED")
print("=" * 60)
