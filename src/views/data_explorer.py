"""Section 5 View: Transaction Ledger & Forensic Data Explorer."""

import pandas as pd
import streamlit as st

from src.components.metrics import render_kpi_card
from src.components.narratives import render_data_dictionary_expander


def render_data_explorer_view(df: pd.DataFrame) -> None:
    """Render Section 5: Full Transaction Ledger & Forensic Data Explorer."""
    st.markdown("## Section 5: Transaction Ledger & Forensic Data Explorer")
    st.markdown(
        "**Audit & Forensic Objective**: Provide institutional transparency and direct transaction-level access "
        "across the complete global order ledger (51,290 records) with multi-criteria filtering, text search, "
        "column configuration, and raw CSV export."
    )
    st.markdown("---")

    # Formal Problem Formulation (Audit & Governance)
    with st.container(border=True):
        st.markdown("### Formal Problem Formulation: Transaction-Level Auditability & Data Integrity Governance")
        st.markdown(
            r"""
            **Forensic Inquiry & Verification Objective**:
            Executive summaries and aggregated business intelligence visualizations often obscure micro-level transaction anomalies, isolated discounting abuses, and operational slippage. 
            Corporate leadership, internal audit, and board committees require an un-aggregated, granular ledger interface to resolve three forensic governance questions:

            1. **Transaction Verifiability**: Can every consolidated deficit be traced back to individual commercial contracts, order IDs, sales representatives, and shipping manifests?
            2. **Exception Isolation**: Which specific commercial transactions breached standard margin, discount (> 20%), and freight absorption guidelines?
            3. **Exportability & Independent Audit**: Can internal and external compliance teams extract filtered, reproducible transaction slices for statutory compliance, tax reconciliation, and audit scrutiny?
            """
        )

    render_data_dictionary_expander()

    if df.empty:
        st.warning("No records match the current global filter selection.")
        return

    # Filter & Search Controls Container
    with st.container(border=True):
        st.markdown("### Forensic Filter & Query Console")

        c_search1, c_search2 = st.columns([2, 1])
        with c_search1:
            search_query = st.text_input(
                "Universal Search (Order ID, Customer Name, Product Name, City)",
                placeholder="e.g. CA-2014-115812, Global Superstore, Tables, Istanbul...",
            )
        with c_search2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            loss_only = st.checkbox("Negative-Margin Records Only (Profit < $0)", value=False)

        c_filt1, c_filt2, c_filt3, c_filt4 = st.columns(4)

        with c_filt1:
            all_markets = sorted(df["Market"].dropna().unique().tolist()) if "Market" in df.columns else []
            selected_markets = st.multiselect("Filter by Market", options=all_markets, default=[])

        with c_filt2:
            # Dynamically filter countries based on selected markets if any
            if selected_markets and "Market" in df.columns and "Country" in df.columns:
                available_countries = sorted(df[df["Market"].isin(selected_markets)]["Country"].dropna().unique().tolist())
            elif "Country" in df.columns:
                available_countries = sorted(df["Country"].dropna().unique().tolist())
            else:
                available_countries = []
            selected_countries = st.multiselect("Filter by Sovereign Territory", options=available_countries, default=[])

        with c_filt3:
            all_cats = sorted(df["Category"].dropna().unique().tolist()) if "Category" in df.columns else []
            selected_cats = st.multiselect("Filter by Category", options=all_cats, default=[])

        with c_filt4:
            if selected_cats and "Category" in df.columns and "Sub-Category" in df.columns:
                available_subcats = sorted(df[df["Category"].isin(selected_cats)]["Sub-Category"].dropna().unique().tolist())
            elif "Sub-Category" in df.columns:
                available_subcats = sorted(df["Sub-Category"].dropna().unique().tolist())
            else:
                available_subcats = []
            selected_subcats = st.multiselect("Filter by Sub-Category", options=available_subcats, default=[])

        c_disc1, c_disc2 = st.columns(2)
        with c_disc1:
            min_disc, max_disc = st.slider(
                "Discount Range Filter (%)",
                min_value=0.0,
                max_value=100.0,
                value=(0.0, 100.0),
                step=5.0,
                help="Filter transactions by contractual discount rate.",
            )
        with c_disc2:
            high_discount_only = st.checkbox(
                "Strict Discount Leakage (Discount > 20.0% Only)",
                value=False,
                help="Quickly isolate transactions executed beyond the 20% inversion threshold.",
            )

    # Apply Local Filters
    filtered = df.copy()

    if search_query.strip():
        q = search_query.strip().lower()
        search_cols = ["Order ID", "Customer Name", "Product Name", "City", "Country"]
        masks = []
        for col in search_cols:
            if col in filtered.columns:
                masks.append(filtered[col].astype(str).str.lower().str.contains(q, na=False))
        if masks:
            combined_mask = masks[0]
            for m in masks[1:]:
                combined_mask |= m
            filtered = filtered[combined_mask]

    if loss_only and "Profit" in filtered.columns:
        filtered = filtered[filtered["Profit"] < 0]

    if high_discount_only and "Discount" in filtered.columns:
        filtered = filtered[filtered["Discount"] > 0.20]

    if min_disc > 0 or max_disc < 100:
        if "Discount" in filtered.columns:
            filtered = filtered[
                (filtered["Discount"] >= min_disc / 100.0) & (filtered["Discount"] <= max_disc / 100.0)
            ]

    if selected_markets and "Market" in filtered.columns:
        filtered = filtered[filtered["Market"].isin(selected_markets)]

    if selected_countries and "Country" in filtered.columns:
        filtered = filtered[filtered["Country"].isin(selected_countries)]

    if selected_cats and "Category" in filtered.columns:
        filtered = filtered[filtered["Category"].isin(selected_cats)]

    if selected_subcats and "Sub-Category" in filtered.columns:
        filtered = filtered[filtered["Sub-Category"].isin(selected_subcats)]

    # Dynamic Filtered Metrics Summary
    st.markdown("<br>", unsafe_allow_html=True)
    f_sales = float(filtered["Sales"].sum()) if "Sales" in filtered.columns else 0.0
    f_profit = float(filtered["Profit"].sum()) if "Profit" in filtered.columns else 0.0
    f_margin = (f_profit / f_sales * 100.0) if f_sales > 0 else 0.0
    f_rows = len(filtered)
    f_loss_rows = int((filtered["Profit"] < 0).sum()) if "Profit" in filtered.columns else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            title="Matching Transactions",
            value=f"{f_rows:,}",
            sub_value=f"{(f_rows / len(df) * 100):.1f}% of Active Universe",
        )
    with k2:
        render_kpi_card(
            title="Invoiced Gross Sales",
            value=f"${f_sales:,.0f}",
            sub_value=f"Avg Line Value: ${(f_sales / f_rows):,.2f}" if f_rows > 0 else "$0.00",
        )
    with k3:
        render_kpi_card(
            title="Operating Contribution",
            value=f"${f_profit:,.0f}",
            sub_value=f"Margin: {f_margin:.2f}%",
        )
    with k4:
        render_kpi_card(
            title="Deficit Order Lines",
            value=f"{f_loss_rows:,}",
            sub_value=f"{(f_loss_rows / f_rows * 100):.1f}% Loss Rate" if f_rows > 0 else "0.0%",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Column Customization & Dataframe Table
    with st.container(border=True):
        col_header_left, col_header_right = st.columns([3, 1])
        with col_header_left:
            st.markdown("### Forensic Transaction Ledger")
        with col_header_right:
            csv_data = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"Export {f_rows:,} Records (CSV)",
                data=csv_data,
                file_name="global_superstore_ledger_export.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Default standard audit columns
        default_cols = [
            "Order ID",
            "Order Date",
            "Market",
            "Country",
            "Customer Name",
            "Segment",
            "Category",
            "Sub-Category",
            "Product Name",
            "Sales",
            "Quantity",
            "Discount",
            "Profit",
            "Shipping Cost",
            "Ship Mode",
            "Order Priority",
        ]
        available_cols = [c for c in default_cols if c in filtered.columns]
        other_cols = [c for c in filtered.columns if c not in default_cols]

        selected_display_cols = st.multiselect(
            "Configure Display Columns",
            options=available_cols + other_cols,
            default=available_cols,
        )

        if not selected_display_cols:
            selected_display_cols = available_cols

        # Format columns using Streamlit column_config (no Pandas Styler cell-count limits)
        col_config: dict = {}
        if "Sales" in selected_display_cols:
            col_config["Sales"] = st.column_config.NumberColumn("Sales", format="$%.2f")
        if "Profit" in selected_display_cols:
            col_config["Profit"] = st.column_config.NumberColumn("Profit", format="$%.2f")
        if "Shipping Cost" in selected_display_cols:
            col_config["Shipping Cost"] = st.column_config.NumberColumn("Shipping Cost", format="$%.2f")
        if "Discount" in selected_display_cols:
            col_config["Discount"] = st.column_config.NumberColumn("Discount", format="%.1f%%")
        if "Quantity" in selected_display_cols:
            col_config["Quantity"] = st.column_config.NumberColumn("Quantity", format="%d")
        if "Profit_Margin" in selected_display_cols:
            col_config["Profit_Margin"] = st.column_config.NumberColumn("Profit Margin", format="%.2f%%")

        st.dataframe(
            filtered[selected_display_cols],
            column_config=col_config,
            use_container_width=True,
            height=500,
        )

    st.divider()

    # Section 5 Proposed Solutions
    with st.container(border=True):
        st.markdown("### Section 5: Data Governance & Operational Integration Solutions")
        st.markdown(
            r"""
            To bridge the gap between analytical forensics and day-to-day enterprise execution, the following data governance solutions are proposed:

            1. **Real-Time ERP Transaction Interceptors**:
               - Embed automated pre-settlement checks directly into the transactional order-entry engine (SAP/Salesforce/NetSuite). Any transaction breaching negative margin thresholds or the 20% discount ceiling must be programmatically flagged for immediate managerial sign-off before fulfillment.

            2. **Automated Audit Exception Logging**:
               - Establish automated daily exception feeds distributed to Regional Controllers and Internal Audit detailing all transactions where discount concessions exceeded 20% or where freight absorption exceeded product gross margin.

            3. **Master Data Catalog & Landed Cost Model Standardization**:
               - Standardize corporate master data catalogs, dimensional weight parameters, and landed cost models across all international operating entities to eliminate shipping cost misallocations and currency translation discrepancies.
            """
        )
