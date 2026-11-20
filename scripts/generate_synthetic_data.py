
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

# Project paths
ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "azure_costs.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Synthetic Azure resources
resources = [
    {
        "name": "vm-prod-01",
        "type": "Microsoft.Compute/virtualMachines",
        "service": "Virtual Machines",
        "family": "Compute",
        "meter": "D2s v5",
        "region": "France Central",
        "unit": "Hours",
        "price": 0.12,
        "environment": "production",
        "owner": "platform",
    },
    {
        "name": "vm-prod-02",
        "type": "Microsoft.Compute/virtualMachines",
        "service": "Virtual Machines",
        "family": "Compute",
        "meter": "D4s v5",
        "region": "West Europe",
        "unit": "Hours",
        "price": 0.24,
        "environment": "production",
        "owner": "backend",
    },
    {
        "name": "vm-dev-01",
        "type": "Microsoft.Compute/virtualMachines",
        "service": "Virtual Machines",
        "family": "Compute",
        "meter": "B2s",
        "region": "France Central",
        "unit": "Hours",
        "price": 0.05,
        "environment": "development",
        "owner": "data",
    },
    {
        "name": "storage-prod-01",
        "type": "Microsoft.Storage/storageAccounts",
        "service": "Storage",
        "family": "Storage",
        "meter": "Hot LRS Capacity",
        "region": "France Central",
        "unit": "GB/Month",
        "price": 0.02,
        "environment": "production",
        "owner": "platform",
    },
    {
        "name": "storage-dev-01",
        "type": "Microsoft.Storage/storageAccounts",
        "service": "Storage",
        "family": "Storage",
        "meter": "Hot LRS Capacity",
        "region": "West Europe",
        "unit": "GB/Month",
        "price": 0.02,
        "environment": "development",
        "owner": "data",
    },
    {
        "name": "sql-prod-01",
        "type": "Microsoft.Sql/servers/databases",
        "service": "Azure SQL Database",
        "family": "Databases",
        "meter": "General Purpose vCore",
        "region": "France Central",
        "unit": "Hours",
        "price": 0.18,
        "environment": "production",
        "owner": "backend",
    },
    {
        "name": "app-prod-01",
        "type": "Microsoft.Web/sites",
        "service": "App Service",
        "family": "Compute",
        "meter": "Basic Plan",
        "region": "West Europe",
        "unit": "Hours",
        "price": 0.08,
        "environment": "production",
        "owner": "backend",
    },
    {
        "name": "network-prod-01",
        "type": "Microsoft.Network/publicIPAddresses",
        "service": "Bandwidth",
        "family": "Networking",
        "meter": "Data Transfer",
        "region": "France Central",
        "unit": "GB",
        "price": 0.04,
        "environment": "production",
        "owner": "platform",
    },
    {
        "name": "vm-test-01",
        "type": "Microsoft.Compute/virtualMachines",
        "service": "Virtual Machines",
        "family": "Compute",
        "meter": "B2s",
        "region": "West Europe",
        "unit": "Hours",
        "price": 0.05,
        "environment": "testing",
        "owner": "qa",
    },
    {
        "name": "sql-dev-01",
        "type": "Microsoft.Sql/servers/databases",
        "service": "Azure SQL Database",
        "family": "Databases",
        "meter": "General Purpose vCore",
        "region": "West Europe",
        "unit": "Hours",
        "price": 0.12,
        "environment": "development",
        "owner": "data",
    },
]

subscriptions = [
    ("sub-001", "Production Subscription"),
    ("sub-002", "Development Subscription"),
]

fields = [
    "Date",
    "SubscriptionId",
    "SubscriptionName",
    "ResourceGroup",
    "ResourceId",
    "ResourceName",
    "ResourceType",
    "ServiceName",
    "ServiceFamily",
    "MeterCategory",
    "MeterName",
    "Region",
    "Quantity",
    "UnitOfMeasure",
    "EffectivePrice",
    "CostInBillingCurrency",
    "BillingCurrency",
    "Tags",
]

start_date = date(2026, 1, 1)
number_of_days = 90

rows = []

for day_offset in range(number_of_days):
    current_date = start_date + timedelta(days=day_offset)

    for index, resource in enumerate(resources):
        subscription_id, subscription_name = subscriptions[
            index % len(subscriptions)
        ]

        # Simulate daily consumption
        if resource["unit"] == "Hours":
            quantity = random.uniform(8, 24)
        elif resource["unit"] == "GB/Month":
            quantity = random.uniform(100, 1000)
        else:
            quantity = random.uniform(10, 500)

        quantity = round(quantity, 2)
        effective_price = resource["price"]

        # Calculate deterministic billing amount
        cost = round(quantity * effective_price, 2)

        resource_group = (
            f"rg-{resource['environment']}-"
            f"{resource['service'].lower().replace(' ', '-')}"
        )

        resource_id = (
            f"/subscriptions/{subscription_id}"
            f"/resourceGroups/{resource_group}"
            f"/providers/{resource['type']}/{resource['name']}"
        )

        tags = {
            "environment": resource["environment"],
            "owner": resource["owner"],
            "project": "CloudMindAI",
        }

        rows.append({
            "Date": current_date.isoformat(),
            "SubscriptionId": subscription_id,
            "SubscriptionName": subscription_name,
            "ResourceGroup": resource_group,
            "ResourceId": resource_id,
            "ResourceName": resource["name"],
            "ResourceType": resource["type"],
            "ServiceName": resource["service"],
            "ServiceFamily": resource["family"],
            "MeterCategory": resource["family"],
            "MeterName": resource["meter"],
            "Region": resource["region"],
            "Quantity": quantity,
            "UnitOfMeasure": resource["unit"],
            "EffectivePrice": effective_price,
            "CostInBillingCurrency": cost,
            "BillingCurrency": "EUR",
            "Tags": json.dumps(tags),
        })

# Write CSV
with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Dataset generated successfully: {OUTPUT_FILE}")
print(f"Number of rows: {len(rows)}")
print(f"Number of columns: {len(fields)}")
print(f"Period: {start_date} to {start_date + timedelta(days=number_of_days - 1)}")
