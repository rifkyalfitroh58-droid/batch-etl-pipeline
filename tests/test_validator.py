import pytest
import pandas as pd

from pipeline.validator import FileValidator


@pytest.fixture
def valid_df():
    return pd.DataFrame({
        "transaction_id":   ["T001", "T002"],
        "customer_id":      ["C1",   "C2"],
        "amount":           [100.0,  200.0],
        "transaction_date": ["2024-01-01", "2024-01-02"],
        "status":           ["completed", "pending"],
    })


def test_valid_data_passes(valid_df):
    result = FileValidator().validate(valid_df, "test.csv")
    assert result.is_valid is True
    assert result.errors == []


def test_missing_column_fails():
    df = pd.DataFrame({"transaction_id": ["T001"]})
    result = FileValidator().validate(df, "test.csv")
    assert result.is_valid is False


def test_null_amount_fails(valid_df):
    valid_df.loc[0, "amount"] = None
    result = FileValidator().validate(valid_df, "test.csv")
    assert result.is_valid is False


def test_invalid_status_fails(valid_df):
    valid_df.loc[0, "status"] = "unknown_status"
    result = FileValidator().validate(valid_df, "test.csv")
    assert result.is_valid is False