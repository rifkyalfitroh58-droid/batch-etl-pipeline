import pytest
import pandas as pd
from pipeline.transformer import DataTransformer


@pytest.fixture
def valid_df():
    return pd.DataFrame({
        "transaction_id":   ["T001", "T002", "T003"],
        "customer_id":      ["  C1 ", "C2",   "C3"],
        "amount":           ["150000", "75000", "200000"],
        "transaction_date": ["2024-01-10", "2024-01-11", "2024-01-12"],
        "status":           ["COMPLETED", "PENDING", " failed "],
    })


def test_transform_returns_dataframe(valid_df):
    result = DataTransformer().transform(valid_df)
    assert isinstance(result, pd.DataFrame)


def test_status_normalized_to_lowercase(valid_df):
    result = DataTransformer().transform(valid_df)
    assert result["status"].tolist() == ["completed", "pending", "failed"]


def test_customer_id_stripped(valid_df):
    result = DataTransformer().transform(valid_df)
    assert result["customer_id"].tolist() == ["C1", "C2", "C3"]


def test_amount_cast_to_numeric(valid_df):
    result = DataTransformer().transform(valid_df)
    assert result["amount"].dtype in ["float64", "int64"]


def test_transaction_date_cast_to_datetime(valid_df):
    result = DataTransformer().transform(valid_df)
    assert pd.api.types.is_datetime64_any_dtype(result["transaction_date"])


def test_duplicates_removed():
    df = pd.DataFrame({
        "transaction_id":   ["T001", "T001", "T002"],
        "customer_id":      ["C1",   "C1",   "C2"],
        "amount":           [100.0,  100.0,  200.0],
        "transaction_date": ["2024-01-01", "2024-01-01", "2024-01-02"],
        "status":           ["completed",  "completed",  "pending"],
    })
    result = DataTransformer().transform(df)
    assert len(result) == 2


def test_original_dataframe_not_modified(valid_df):
    original_status = valid_df["status"].tolist()
    DataTransformer().transform(valid_df)
    assert valid_df["status"].tolist() == original_status