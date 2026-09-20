"""Sidebar filtering controls for Global Superstore."""

from typing import Any
import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> dict[str, Any]:
    """Render institutional filtering controls for Global Superstore in the sidebar.

    Args:
        df: The active pandas DataFrame.

    Returns:
        Dictionary containing user-selected filter parameters.
    """
    st.sidebar.markdown("### Commercial Filter Controls")

    # 1. Year Filter
    selected_years = []
    if "Year" in df.columns:
        all_years = sorted(df["Year"].dropna().unique().astype(int).tolist())
        selected_years = st.sidebar.multiselect(
            "Fiscal Year Selection",
            options=all_years,
            default=all_years,
        )

    # 2. Market Filter
    selected_markets = []
    if "Market" in df.columns:
        all_markets = sorted(df["Market"].dropna().unique().tolist())
        selected_markets = st.sidebar.multiselect(
            "Geographic Operating Theater",
            options=all_markets,
            default=all_markets,
        )

    # 3. Category Filter
    selected_categories = []
    if "Category" in df.columns:
        all_categories = sorted(df["Category"].dropna().unique().tolist())
        selected_categories = st.sidebar.multiselect(
            "Merchandise Division",
            options=all_categories,
            default=all_categories,
        )

    # 4. Customer Segment Filter
    selected_segments = []
    if "Segment" in df.columns:
        all_segments = sorted(df["Segment"].dropna().unique().tolist())
        selected_segments = st.sidebar.multiselect(
            "Customer Account Tier",
            options=all_segments,
            default=all_segments,
        )

    # 5. Optional Date Range
    selected_date_range = None
    if "Order Date" in df.columns and not df["Order Date"].dropna().empty:
        min_date = df["Order Date"].min().date()
        max_date = df["Order Date"].max().date()

        with st.sidebar.expander("Date Range Parameters", expanded=False):
            selected_date_range = st.date_input(
                "Order Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"Active Transaction Ledger: {len(df):,} line items."
    )

    return {
        "years": selected_years,
        "markets": selected_markets,
        "categories": selected_categories,
        "segments": selected_segments,
        "date_range": selected_date_range,
    }
