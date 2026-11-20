
import pandas as pd
import pytest

from pipeline.transform import transform_data
from pipeline.validate import validate_data


@pytest.fixture
def sample_data():
    """Small, clean dataset used by automated tests."""

    return pd.DataFrame([
        {
            "Date": "2026-01-01",
            "SubscriptionId": "sub-001",
            "SubscriptionName": "Production",
            "ResourceGroup": "rg-prod-compute",
            "ResourceId": "/subscriptions/sub-001/vm/vm-01",
            "ResourceName": "vm-01",
            "ResourceType": "Microsoft.Compute/virtualMachines",
            "ServiceName": "Virtual Machines",
            "ServiceFamily": "Compute",
            "MeterCategory": "Compute",
            "MeterName": "D2s v5",
            "Region": "France Central",
            "Quantity": 10,
            "UnitOfMeasure": "Hours",
            "EffectivePrice": 0.12,
            "CostInBillingCurrency": 1.20,
            "BillingCurrency": "EUR",
            "Tags": '{"environment": "production"}',
        },
        {
            "Date": "2026-01-02",
            "SubscriptionId": "sub-001",
            "SubscriptionName": "Production",
            "ResourceGroup": "rg-prod-compute",
            "ResourceId": "/subscriptions/sub-001/vm/vm-02",
            "ResourceName": "vm-02",
            "ResourceType": "Microsoft.Compute/virtualMachines",
            "ServiceName": "Virtual Machines",
            "ServiceFamily": "Compute",
            "MeterCategory": "Compute",
            "MeterName": "D2s v5",
            "Region": "France Central",
            "Quantity": 20,
            "UnitOfMeasure": "Hours",
            "EffectivePrice": 0.12,
            "CostInBillingCurrency": 2.40,
            "BillingCurrency": "EUR",
            "Tags": '{"environment": "development"}',
        },
    ])


# -------------------------------------------
# TEST 1 - Transformation
# -------------------------------------------

def test_transform_converts_dates_and_numeric_values(sample_data):
    result = transform_data(sample_data)

    assert pd.api.types.is_datetime64_any_dtype(result["Date"])
    assert pd.api.types.is_numeric_dtype(result["Quantity"])
    assert pd.api.types.is_numeric_dtype(result["EffectivePrice"])
    assert pd.api.types.is_numeric_dtype(result["CostInBillingCurrency"])


# -------------------------------------------
# TEST 2 - Valid dataset
# -------------------------------------------

def test_valid_dataset_has_no_rejected_rows(sample_data):
    transformed = transform_data(sample_data)

    valid, rejected, report = validate_data(transformed)

    assert len(valid) == 2
    assert len(rejected) == 0


# -------------------------------------------
# TEST 3 - Negative costs
# -------------------------------------------

def test_negative_cost_is_rejected(sample_data):
    sample_data.loc[0, "CostInBillingCurrency"] = -10

    transformed = transform_data(sample_data)

    valid, rejected, report = validate_data(transformed)

    assert len(rejected) == 1
    assert len(valid) == 1
    assert "Negative" in rejected.iloc[0]["RejectionReason"]


# -------------------------------------------
# TEST 4 - Invalid numeric values
# -------------------------------------------

def test_invalid_quantity_is_rejected(sample_data):
    sample_data.loc[0, "Quantity"] = "abc"

    transformed = transform_data(sample_data)

    valid, rejected, report = validate_data(transformed)

    assert len(rejected) == 1
    assert len(valid) == 1
    assert "Invalid numeric value" in rejected.iloc[0]["RejectionReason"]


# -------------------------------------------
# TEST 5 - Duplicate business key
# -------------------------------------------

def test_duplicate_business_key_is_rejected(sample_data):
    sample_data.loc[1] = sample_data.loc[0].copy()

    transformed = transform_data(sample_data)

    valid, rejected, report = validate_data(transformed)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert "Duplicate business key" in rejected.iloc[0]["RejectionReason"]


# -------------------------------------------
# TEST 6 - Inconsistent cost calculation
# -------------------------------------------

def test_inconsistent_cost_is_rejected(sample_data):
    sample_data.loc[0, "CostInBillingCurrency"] = 999

    transformed = transform_data(sample_data)

    valid, rejected, report = validate_data(transformed)

    assert len(rejected) == 1
    assert len(valid) == 1
    assert "Cost calculation mismatch" in rejected.iloc[0]["RejectionReason"]
