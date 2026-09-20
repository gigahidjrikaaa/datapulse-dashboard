"""Unit tests for the data_loader service with Global Superstore schema."""

import io
import pandas as pd
import pytest

from src.services.data_loader import (
    load_sales_data,
    preprocess_data,
    validate_dataframe,
)


def test_preprocess_data_derived_columns() -> None:
    """Ensure date parts, profit margin, and discount buckets are correctly derived."""
    raw = pd.DataFrame(
        {
            "Order Date": ["15-01-2014", "20-02-2014"],
            "Ship Date": ["18-01-2014", "24-02-2014"],
            "Sales": [100.0, 200.0],
            "Profit": [20.0, -50.0],
            "Discount": [0.1, 0.4],
            "Shipping Cost": [10.0, 30.0],
            "Quantity": [2, 4],
        }
    )
    processed = preprocess_data(raw)

    assert "Profit_Margin" in processed.columns
    assert processed["Profit_Margin"].iloc[0] == pytest.approx(20.0)
    assert processed["Profit_Margin"].iloc[1] == pytest.approx(-25.0)
    assert processed["Is_Loss"].iloc[0] is False or processed["Is_Loss"].iloc[0] == 0
    assert processed["Is_Loss"].iloc[1] is True or processed["Is_Loss"].iloc[1] == 1
    assert processed["Year"].iloc[0] == 2014
    assert processed["Shipping_Days"].iloc[0] == 3
    assert "Discount_Bucket" in processed.columns


def test_validate_dataframe_columns() -> None:
    """Verify validation detects missing required Global Superstore columns."""
    incomplete_df = pd.DataFrame({"Order ID": ["ORD-1"], "Sales": [100.0]})
    is_valid, missing = validate_dataframe(incomplete_df)
    assert is_valid is False
    assert len(missing) > 0


def test_load_sales_data_from_buffer() -> None:
    """Test loading data from an in-memory CSV buffer with latin1 encoding."""
    csv_content = (
        "Row ID,Order ID,Order Date,Ship Date,Ship Mode,Customer ID,Customer Name,Segment,"
        "City,State,Country,Market,Region,Product ID,Category,Sub-Category,Product Name,"
        "Sales,Quantity,Discount,Profit,Shipping Cost,Order Priority\n"
        "1,ORD-1,01-01-2014,03-01-2014,Standard,C-1,Jane Doe,Consumer,Paris,Ile-de-France,France,"
        "EU,Central,P-1,Technology,Phones,Smart Phone,500.0,2,0.1,100.0,25.0,High\n"
    )
    buf = io.BytesIO(csv_content.encode("latin1"))
    df = load_sales_data(buf)

    assert len(df) == 1
    assert df["Order ID"].iloc[0] == "ORD-1"
    assert df["Profit"].iloc[0] == 100.0
    assert df["Profit_Margin"].iloc[0] == pytest.approx(20.0)


def test_load_sales_data_missing_file() -> None:
    """Ensure missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_sales_data("non_existent_dataset.csv")
