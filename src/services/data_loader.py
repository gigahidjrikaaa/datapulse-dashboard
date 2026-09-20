"""Data loading and caching service for the Global Superstore dataset."""

from pathlib import Path
from typing import BinaryIO, Union
import pandas as pd
import streamlit as st

from src.config import DEFAULT_DATASET_PATH, REQUIRED_COLUMNS


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate whether the dataframe contains all expected required columns.

    Args:
        df: Input pandas DataFrame.

    Returns:
        A tuple of (is_valid, missing_columns).
    """
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing_cols) == 0, missing_cols


def preprocess_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich Global Superstore data.

    Parses dates, standardizes types, and derives metrics for analysis.

    Args:
        raw_df: Raw input DataFrame.

    Returns:
        Cleaned, enriched DataFrame with temporal and financial derivations.
    """
    df = raw_df.copy()

    # Parse Order Date and Ship Date with dayfirst format (DD-MM-YYYY)
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", errors="coerce")
        # Fallback if any failed
        if df["Order Date"].isnull().any():
            df["Order Date"] = df["Order Date"].fillna(
                pd.to_datetime(raw_df["Order Date"], dayfirst=True, errors="coerce")
            )
        df["Year"] = df["Order Date"].dt.year
        df["Month"] = df["Order Date"].dt.strftime("%Y-%m")
        df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
        df["Day_Name"] = df["Order Date"].dt.day_name()

    if "Ship Date" in df.columns:
        df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y", errors="coerce")
        if df["Ship Date"].isnull().any():
            df["Ship Date"] = df["Ship Date"].fillna(
                pd.to_datetime(raw_df["Ship Date"], dayfirst=True, errors="coerce")
            )

    if "Order Date" in df.columns and "Ship Date" in df.columns:
        df["Shipping_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

    # Ensure numeric columns
    numeric_cols = ["Sales", "Quantity", "Discount", "Profit", "Shipping Cost"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Financial & Loss derivations
    if "Profit" in df.columns and "Sales" in df.columns:
        df["Profit_Margin"] = (
            df["Profit"] / df["Sales"].replace(0, float("nan"))
        ).fillna(0.0) * 100.0
        df["Is_Loss"] = df["Profit"] < 0

    if "Discount" in df.columns:
        df["Discount_Pct"] = df["Discount"] * 100.0
        bins = [-0.01, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
        labels = ["0%", "0.1-10%", "10.1-20%", "20.1-30%", "30.1-40%", "40.1-50%", ">50%"]
        df["Discount_Bucket"] = pd.cut(df["Discount"], bins=bins, labels=labels)

    if "Shipping Cost" in df.columns and "Sales" in df.columns:
        df["Shipping_Cost_Ratio"] = (
            df["Shipping Cost"] / df["Sales"].replace(0, float("nan"))
        ).fillna(0.0) * 100.0

    return df


@st.cache_data(show_spinner="Loading and parsing Global Superstore dataset...")
def load_sales_data(source: Union[str, Path, BinaryIO, None] = None) -> pd.DataFrame:
    """Load and cache the Global Superstore dataset from file path or uploaded buffer.

    Supports CSV (with latin1/utf-8 encoding fallbacks) and Excel (.xlsx).

    Args:
        source: Optional file path or uploaded file buffer. Defaults to DEFAULT_DATASET_PATH.

    Returns:
        Preprocessed and enriched DataFrame.

    Raises:
        FileNotFoundError: If dataset does not exist on disk.
        ValueError: If file is empty or cannot be parsed.
    """
    target = source if source is not None else DEFAULT_DATASET_PATH

    raw_df: pd.DataFrame
    if isinstance(target, (str, Path)):
        path_obj = Path(target)
        if not path_obj.exists():
            raise FileNotFoundError(f"Dataset not found at: {path_obj.resolve()}")

        if path_obj.suffix.lower() in [".xlsx", ".xls"]:
            raw_df = pd.read_excel(path_obj)
        else:
            try:
                raw_df = pd.read_csv(path_obj, encoding="latin1")
            except Exception:
                try:
                    raw_df = pd.read_csv(path_obj, encoding="utf-8")
                except Exception:
                    raw_df = pd.read_csv(path_obj, encoding="cp1252")
    else:
        # Buffer / uploaded file
        try:
            raw_df = pd.read_csv(target, encoding="latin1")
        except Exception:
            try:
                target.seek(0)
                raw_df = pd.read_excel(target)
            except Exception:
                target.seek(0)
                raw_df = pd.read_csv(target, encoding="utf-8")

    if raw_df.empty:
        raise ValueError("The provided dataset is empty.")

    return preprocess_data(raw_df)
