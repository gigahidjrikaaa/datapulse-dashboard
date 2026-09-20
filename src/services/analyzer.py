"""Analytical service for Global Superstore Revival Strategy tasks."""

from typing import Any, Optional, Sequence
import numpy as np
import pandas as pd


def compute_overview_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Calculate executive KPI metrics for Global Superstore.

    Args:
        df: Filtered or full DataFrame.

    Returns:
        Dictionary of formatted summary KPIs.
    """
    if df.empty:
        return {
            "total_sales": 0.0,
            "total_profit": 0.0,
            "profit_margin": 0.0,
            "total_orders": 0.0,
            "total_quantity": 0.0,
            "loss_order_count": 0.0,
            "loss_order_pct": 0.0,
            "profit_loss_drag": 0.0,
            "profitable_order_gain": 0.0,
            "total_shipping_cost": 0.0,
        }

    total_sales = float(df["Sales"].sum()) if "Sales" in df.columns else 0.0
    total_profit = float(df["Profit"].sum()) if "Profit" in df.columns else 0.0
    profit_margin = (total_profit / total_sales * 100.0) if total_sales > 0 else 0.0
    total_orders = float(df["Order ID"].nunique()) if "Order ID" in df.columns else float(len(df))
    total_quantity = float(df["Quantity"].sum()) if "Quantity" in df.columns else 0.0
    total_shipping = float(df["Shipping Cost"].sum()) if "Shipping Cost" in df.columns else 0.0

    # Profit vs Loss segmentation
    loss_mask = df["Profit"] < 0
    loss_order_count = float(loss_mask.sum())
    loss_order_pct = (loss_order_count / len(df) * 100.0) if len(df) > 0 else 0.0
    profit_loss_drag = float(abs(df[loss_mask]["Profit"].sum())) if loss_mask.any() else 0.0
    profitable_gain = float(df[~loss_mask]["Profit"].sum()) if (~loss_mask).any() else 0.0

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "loss_order_count": loss_order_count,
        "loss_order_pct": loss_order_pct,
        "profit_loss_drag": profit_loss_drag,
        "profitable_order_gain": profitable_gain,
        "total_shipping_cost": total_shipping,
    }


def compute_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Task 1 Year-over-Year (YoY) Sales, Profit, and Margin growth.

    Args:
        df: Input DataFrame containing 'Year', 'Sales', 'Profit'.

    Returns:
        DataFrame summarizing 2011-2014 metrics and YoY percentage changes.
    """
    if df.empty or "Year" not in df.columns:
        return pd.DataFrame()

    yearly = (
        df.groupby("Year")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Line_Items=("Row ID", "count"),
            Quantity=("Quantity", "sum"),
        )
        .reset_index()
    )

    yearly["Profit_Margin"] = (yearly["Profit"] / yearly["Sales"]) * 100.0
    yearly["Sales_YoY_Growth"] = yearly["Sales"].pct_change() * 100.0
    yearly["Profit_YoY_Growth"] = yearly["Profit"].pct_change() * 100.0
    yearly["Orders_YoY_Growth"] = yearly["Orders"].pct_change() * 100.0
    yearly["Avg_Order_Value"] = yearly["Sales"] / yearly["Orders"]

    return yearly


def compute_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly Sales and Profit trends.

    Args:
        df: Input DataFrame containing 'Order Date', 'Sales', 'Profit'.

    Returns:
        Aggregated monthly DataFrame sorted by date.
    """
    if df.empty or "Order Date" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()
    temp["Period"] = temp["Order Date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        temp.groupby("Period", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Shipping_Cost=("Shipping Cost", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .sort_values("Period")
    )
    monthly["Profit_Margin"] = (monthly["Profit"] / monthly["Sales"]) * 100.0
    return monthly


def analyze_geographic_drilldown(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Perform Task 2 geographic drilldown: Market -> Region -> Country.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of (market_summary, region_summary, country_summary).
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    def _summarize_geo(col: str) -> pd.DataFrame:
        if col not in df.columns:
            return pd.DataFrame()
        summary = (
            df.groupby(col, as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Shipping_Cost=("Shipping Cost", "sum"),
                Orders=("Order ID", "nunique"),
                Avg_Discount=("Discount", "mean"),
            )
            .sort_values(by="Profit", ascending=False)
        )
        summary["Profit_Margin"] = (
            summary["Profit"] / summary["Sales"].replace(0, float("nan"))
        ).fillna(0.0) * 100.0
        summary["Avg_Discount_Pct"] = summary["Avg_Discount"] * 100.0
        return summary

    market_df = _summarize_geo("Market")
    region_df = _summarize_geo("Region")
    country_df = _summarize_geo("Country")

    return market_df, region_df, country_df


def compute_quarterly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Compute quarterly seasonality metrics (Q1-Q4) across fiscal years.

    Evaluates intra-year cyclical cadence and validates fourth-quarter volume concentration.

    Args:
        df: Input DataFrame with 'Order Date', 'Sales', 'Profit'.

    Returns:
        DataFrame aggregated by Year and Quarter with Sales, Profit, Margin, and Annual Revenue Share %.
    """
    if df.empty or "Order Date" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()
    temp["Year"] = temp["Order Date"].dt.year
    temp["Quarter_Num"] = "Q" + temp["Order Date"].dt.quarter.astype(str)

    quarterly = (
        temp.groupby(["Year", "Quarter_Num"], as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique") if "Order ID" in temp.columns else ("Sales", "count"),
        )
        .sort_values(by=["Year", "Quarter_Num"])
    )

    annual_sales = quarterly.groupby("Year")["Sales"].transform("sum")
    quarterly["Quarter_Share_Pct"] = (quarterly["Sales"] / annual_sales) * 100.0
    quarterly["Profit_Margin"] = (
        quarterly["Profit"] / quarterly["Sales"].replace(0, np.nan)
    ).fillna(0.0) * 100.0

    return quarterly


def analyze_product_breakdown(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Perform Task 2 product drilldown: Category -> Sub-Category.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of (category_summary, subcategory_summary).
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    def _summarize_prod(col: str) -> pd.DataFrame:
        if col not in df.columns:
            return pd.DataFrame()
        summary = (
            df.groupby(col, as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Quantity=("Quantity", "sum"),
                Avg_Discount=("Discount", "mean"),
                Line_Items=("Row ID", "count"),
            )
            .sort_values(by="Profit", ascending=True)
        )
        summary["Profit_Margin"] = (
            summary["Profit"] / summary["Sales"].replace(0, float("nan"))
        ).fillna(0.0) * 100.0
        summary["Avg_Discount_Pct"] = summary["Avg_Discount"] * 100.0
        return summary

    cat_df = _summarize_prod("Category").sort_values(by="Profit", ascending=False)
    subcat_df = _summarize_prod("Sub-Category")

    return cat_df, subcat_df


def analyze_discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze Task 3 discount tiers and pinpoint the profitability tipping point.

    Args:
        df: Input DataFrame with 'Discount_Bucket' and 'Profit'.

    Returns:
        Aggregated metrics per discount bucket.
    """
    if df.empty or "Discount_Bucket" not in df.columns:
        return pd.DataFrame()

    disc_summary = (
        df.groupby("Discount_Bucket", observed=False)
        .agg(
            Order_Lines=("Row ID", "count"),
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Avg_Profit_Per_Line=("Profit", "mean"),
            Avg_Sales_Per_Line=("Sales", "mean"),
        )
        .reset_index()
    )
    disc_summary["Profit_Margin"] = (
        disc_summary["Total_Profit"] / disc_summary["Total_Sales"].replace(0, float("nan"))
    ).fillna(0.0) * 100.0

    return disc_summary


def analyze_shipping_and_priority(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Analyze Task 3 shipping costs across Ship Modes and Order Priorities.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of (ship_mode_summary, priority_summary).
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    def _summarize_dimension(col: str) -> pd.DataFrame:
        if col not in df.columns:
            return pd.DataFrame()
        summary = (
            df.groupby(col, as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Shipping_Cost=("Shipping Cost", "sum"),
                Avg_Shipping_Cost=("Shipping Cost", "mean"),
                Avg_Shipping_Days=("Shipping_Days", "mean") if "Shipping_Days" in df.columns else ("Shipping Cost", "count"),
                Orders=("Order ID", "nunique"),
            )
            .sort_values(by="Sales", ascending=False)
        )
        summary["Profit_Margin"] = (
            summary["Profit"] / summary["Sales"].replace(0, float("nan"))
        ).fillna(0.0) * 100.0
        summary["Ship_Cost_Ratio"] = (
            summary["Shipping_Cost"] / summary["Sales"].replace(0, float("nan"))
        ).fillna(0.0) * 100.0
        return summary

    ship_mode_df = _summarize_dimension("Ship Mode")
    priority_df = _summarize_dimension("Order Priority")

    return ship_mode_df, priority_df



def filter_data(
    df: pd.DataFrame,
    date_range: Optional[tuple[Any, Any]] = None,
    markets: Optional[Sequence[str]] = None,
    regions: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
    segments: Optional[Sequence[str]] = None,
    years: Optional[Sequence[int]] = None,
) -> pd.DataFrame:
    """Filter Global Superstore DataFrame according to user selected criteria.

    Args:
        df: Input DataFrame.
        date_range: Optional tuple of (start_date, end_date).
        markets: Optional list of selected markets.
        regions: Optional list of selected regions.
        categories: Optional list of selected categories.
        segments: Optional list of selected customer segments.
        years: Optional list of selected years.

    Returns:
        Filtered DataFrame copy.
    """
    filtered = df.copy()

    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        if start_date is not None and end_date is not None and "Order Date" in filtered.columns:
            start_ts = pd.to_datetime(start_date)
            end_ts = pd.to_datetime(end_date)
            filtered = filtered[
                (filtered["Order Date"] >= start_ts) & (filtered["Order Date"] <= end_ts)
            ]

    if years and "Year" in filtered.columns:
        filtered = filtered[filtered["Year"].isin(years)]

    if markets and "Market" in filtered.columns:
        filtered = filtered[filtered["Market"].isin(markets)]

    if regions and "Region" in filtered.columns:
        filtered = filtered[filtered["Region"].isin(regions)]

    if categories and "Category" in filtered.columns:
        filtered = filtered[filtered["Category"].isin(categories)]

    if segments and "Segment" in filtered.columns:
        filtered = filtered[filtered["Segment"].isin(segments)]

    return filtered


def compute_territory_quadrant_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Classify operating territories into 4 strategic portfolio quadrants.

    Framework (McKinsey / BCG 2x2 Matrix):
    1. Core Value Engine: High Sales, High Operating Margin (>= 10.0%).
    2. Margin-Diluted Volume Channel: High Sales, Low/Marginal Margin (< 10.0% but profitable).
    3. High-Yield Niche Profit Center: Moderate/Lower Sales, High Operating Margin (>= 10.0%).
    4. Deficit Rationalization Priority: Negative Operating Profit (< 0.0%).
    5. Secondary Developing Territory: Moderate/Lower Sales, Low/Marginal Margin (< 10.0% but profitable).

    Args:
        df: Input sales DataFrame.

    Returns:
        DataFrame aggregated by Country with quadrant assignments and metrics.
    """
    if df.empty or "Country" not in df.columns:
        return pd.DataFrame()

    agg_dict: dict[str, Any] = {
        "Sales": ("Sales", "sum"),
        "Profit": ("Profit", "sum"),
        "Orders": ("Order ID", "nunique") if "Order ID" in df.columns else ("Sales", "count"),
        "Avg_Discount": ("Discount", "mean") if "Discount" in df.columns else ("Sales", lambda x: 0.0),
    }
    if "Market" in df.columns:
        agg_dict["Market"] = ("Market", "first")

    country_grp = df.groupby("Country", as_index=False).agg(**agg_dict)

    if "Market" not in country_grp.columns:
        country_grp["Market"] = "Global"

    country_grp["Operating_Margin"] = (
        country_grp["Profit"] / country_grp["Sales"].replace(0, np.nan)
    ).fillna(0.0) * 100.0
    country_grp["Profit_Margin"] = country_grp["Operating_Margin"]
    country_grp["Avg_Discount_Pct"] = country_grp["Avg_Discount"] * 100.0

    # Determine Sales Volume Median threshold for High vs Moderate/Lower Sales
    sales_threshold = country_grp["Sales"].median() if len(country_grp) > 1 else 0.0
    margin_threshold = 10.0

    def assign_quadrant(row: pd.Series) -> str:
        if row["Profit"] < 0:
            return "Deficit Rationalization Priority"
        if row["Sales"] >= sales_threshold:
            if row["Operating_Margin"] >= margin_threshold:
                return "Core Value Engine"
            return "Margin-Diluted Volume Channel"
        else:
            if row["Operating_Margin"] >= margin_threshold:
                return "High-Yield Niche Profit Center"
            return "Secondary Developing Territory"

    country_grp["Portfolio_Quadrant"] = country_grp.apply(assign_quadrant, axis=1)
    return country_grp.sort_values(by="Sales", ascending=False)


def simulate_turnaround_impact(
    df: pd.DataFrame,
    max_discount_cap: float = 0.20,
    restructure_deficit_territories: bool = True,
    table_freight_surcharge: float = 15.0,
    volume_attrition_rate: float = 0.05,
) -> dict[str, Any]:
    """Simulate the financial impact of strategic turnaround policy levers.

    Models:
    1. Pricing Governance: Caps discounts exceeding `max_discount_cap`, recovering pricing margin.
    2. International Restructuring: Restructures chronic sovereign deficit territories (Turkey, Nigeria)
       via localized 3PL master distributor model, recovering operating losses.
    3. Freight Pass-Through: Applies dimensional freight surcharges to bulky Tables transactions.
    4. Volume Churn Sensitivity: Deducts elasticity friction penalty from accounts churning due to capped discounts.

    Args:
        df: Input transactions DataFrame.
        max_discount_cap: Maximum allowed discount (e.g. 0.20 for 20%).
        restructure_deficit_territories: If True, restructures Turkey and Nigeria operations.
        table_freight_surcharge: Dollar pass-through surcharge per bulky table unit/order.
        volume_attrition_rate: Simulated customer churn percentage on discount-capped transactions.

    Returns:
        Dictionary containing baseline metrics, projected metrics, and waterfall bridge components.
    """
    if df.empty:
        return {
            "baseline_sales": 0.0,
            "baseline_profit": 0.0,
            "baseline_margin": 0.0,
            "projected_sales": 0.0,
            "projected_profit": 0.0,
            "projected_margin": 0.0,
            "net_ebitda_uplift": 0.0,
            "affected_orders_count": 0,
            "pricing_recovery": 0.0,
            "territory_recovery": 0.0,
            "table_freight_recovery": 0.0,
            "attrition_drag": 0.0,
            "bridge_components": {},
        }

    baseline_sales = float(df["Sales"].sum())
    baseline_profit = float(df["Profit"].sum())
    baseline_margin = (baseline_profit / baseline_sales * 100.0) if baseline_sales > 0 else 0.0

    # 1. Pricing Discipline: Cap discounts above max_discount_cap
    capped_mask = df["Discount"] > max_discount_cap
    affected_orders_count = int(capped_mask.sum())

    if affected_orders_count > 0:
        safe_one_minus_disc = (1.0 - df.loc[capped_mask, "Discount"]).replace(0, 0.001)
        original_list_prices = df.loc[capped_mask, "Sales"] / safe_one_minus_disc
        new_sales_capped = original_list_prices * (1.0 - max_discount_cap)
        pricing_recovery = float((new_sales_capped - df.loc[capped_mask, "Sales"]).sum())
        affected_sales_volume = float(df.loc[capped_mask, "Sales"].sum())
    else:
        pricing_recovery = 0.0
        affected_sales_volume = 0.0

    # 2. Volume Attrition Friction Drag (Price Elasticity Penalty)
    attrition_drag = float(volume_attrition_rate * affected_sales_volume * 0.25)
    lost_sales_attrition = float(volume_attrition_rate * affected_sales_volume)

    # 3. International 3PL Model Restructuring (Turkey & Nigeria)
    if restructure_deficit_territories and "Country" in df.columns:
        deficit_mask = df["Country"].isin(["Turkey", "Nigeria"])
        deficit_profit = float(df.loc[deficit_mask, "Profit"].sum())
        territory_recovery = abs(deficit_profit) if deficit_profit < 0 else 0.0
    else:
        territory_recovery = 0.0

    # 4. Bulky Merchandise Freight Pass-Through (Tables)
    if table_freight_surcharge > 0 and "Sub-Category" in df.columns:
        table_mask = df["Sub-Category"] == "Tables"
        if "Quantity" in df.columns:
            table_units = float(df.loc[table_mask, "Quantity"].sum())
            table_freight_recovery = table_units * table_freight_surcharge
        else:
            table_orders = float(table_mask.sum())
            table_freight_recovery = table_orders * table_freight_surcharge
    else:
        table_freight_recovery = 0.0

    # Net Projected Financials
    projected_profit = (
        baseline_profit
        + pricing_recovery
        + territory_recovery
        + table_freight_recovery
        - attrition_drag
    )
    projected_sales = baseline_sales + pricing_recovery - lost_sales_attrition
    projected_margin = (projected_profit / projected_sales * 100.0) if projected_sales > 0 else 0.0
    net_ebitda_uplift = projected_profit - baseline_profit

    bridge_components = {
        "Baseline Operating Profit": baseline_profit,
        "Pricing Governance (Discount Cap)": pricing_recovery,
        "International 3PL Restructuring": territory_recovery,
        "Tables Freight Pass-Through": table_freight_recovery,
        "Volume Churn Friction Drag": -attrition_drag,
        "Projected Operating EBITDA": projected_profit,
    }

    return {
        "baseline_sales": baseline_sales,
        "baseline_profit": baseline_profit,
        "baseline_margin": baseline_margin,
        "projected_sales": projected_sales,
        "projected_profit": projected_profit,
        "projected_margin": projected_margin,
        "net_ebitda_uplift": net_ebitda_uplift,
        "affected_orders_count": affected_orders_count,
        "pricing_recovery": pricing_recovery,
        "territory_recovery": territory_recovery,
        "table_freight_recovery": table_freight_recovery,
        "attrition_drag": attrition_drag,
        "bridge_components": bridge_components,
    }


def compute_scenario_sensitivity_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pre-compute three institutional turnaround policy scenarios for Board evaluation.

    Scenarios:
    1. Conservative Case: 25% Discount Cap, $0 Table Surcharge, 7.0% Churn Attrition, Partial Restructuring (50% recovery).
    2. Base Case (Recommended Plan): 20% Discount Cap, $15 Table Surcharge, 5.0% Churn Attrition, Full Restructuring.
    3. Aggressive Case: 15% Discount Cap, $25 Table Surcharge, 3.0% Churn Attrition, Full Restructuring.

    Args:
        df: Input master transactions DataFrame.

    Returns:
        Summary DataFrame comparing scenario levers and projected financial outcomes.
    """
    if df.empty:
        return pd.DataFrame()

    baseline_profit = float(df["Profit"].sum()) if "Profit" in df.columns else 0.0
    baseline_sales = float(df["Sales"].sum()) if "Sales" in df.columns else 0.0
    baseline_margin = (baseline_profit / baseline_sales * 100.0) if baseline_sales > 0 else 0.0

    # 1. Conservative Case
    res_cons = simulate_turnaround_impact(
        df=df,
        max_discount_cap=0.25,
        restructure_deficit_territories=False,
        table_freight_surcharge=0.0,
        volume_attrition_rate=0.07,
    )
    turkey_nigeria_deficit = 0.0
    if "Country" in df.columns and "Profit" in df.columns:
        deficit_mask = df["Country"].isin(["Turkey", "Nigeria"]) & (df["Profit"] < 0)
        turkey_nigeria_deficit = float(abs(df.loc[deficit_mask, "Profit"].sum()))
    cons_profit = res_cons["projected_profit"] + (0.50 * turkey_nigeria_deficit)
    cons_uplift = cons_profit - baseline_profit
    cons_margin = (cons_profit / res_cons["projected_sales"] * 100.0) if res_cons["projected_sales"] > 0 else 0.0
    cons_pct_uplift = (cons_uplift / baseline_profit * 100.0) if baseline_profit > 0 else 0.0

    # 2. Base Case (Recommended Plan)
    res_base = simulate_turnaround_impact(
        df=df,
        max_discount_cap=0.20,
        restructure_deficit_territories=True,
        table_freight_surcharge=15.0,
        volume_attrition_rate=0.05,
    )
    base_profit = res_base["projected_profit"]
    base_uplift = res_base["net_ebitda_uplift"]
    base_margin = res_base["projected_margin"]
    base_pct_uplift = (base_uplift / baseline_profit * 100.0) if baseline_profit > 0 else 0.0

    # 3. Aggressive Case
    res_aggr = simulate_turnaround_impact(
        df=df,
        max_discount_cap=0.15,
        restructure_deficit_territories=True,
        table_freight_surcharge=25.0,
        volume_attrition_rate=0.03,
    )
    aggr_profit = res_aggr["projected_profit"]
    aggr_uplift = res_aggr["net_ebitda_uplift"]
    aggr_margin = res_aggr["projected_margin"]
    aggr_pct_uplift = (aggr_uplift / baseline_profit * 100.0) if baseline_profit > 0 else 0.0

    scenarios = [
        {
            "Strategic Scenario": "Baseline (Status Quo)",
            "Discount Cap": "No Cap",
            "Table Surcharge": "$0 / Unit",
            "International Model": "Direct Fulfillment (Deficit)",
            "Churn Attrition": "0.0%",
            "Repriced Orders": 0,
            "Projected Operating EBITDA": baseline_profit,
            "Net EBITDA Uplift": 0.0,
            "EBITDA Uplift (%)": 0.0,
            "Projected Operating Margin": baseline_margin,
        },
        {
            "Strategic Scenario": "1. Conservative Case",
            "Discount Cap": "25.0%",
            "Table Surcharge": "$0 / Unit",
            "International Model": "Hybrid / Partial 3PL (50%)",
            "Churn Attrition": "7.0%",
            "Repriced Orders": res_cons["affected_orders_count"],
            "Projected Operating EBITDA": cons_profit,
            "Net EBITDA Uplift": cons_uplift,
            "EBITDA Uplift (%)": cons_pct_uplift,
            "Projected Operating Margin": cons_margin,
        },
        {
            "Strategic Scenario": "2. Base Case (Recommended Plan)",
            "Discount Cap": "20.0%",
            "Table Surcharge": "$15 / Unit",
            "International Model": "Bonded 3PL Master Distributor",
            "Churn Attrition": "5.0%",
            "Repriced Orders": res_base["affected_orders_count"],
            "Projected Operating EBITDA": base_profit,
            "Net EBITDA Uplift": base_uplift,
            "EBITDA Uplift (%)": base_pct_uplift,
            "Projected Operating Margin": base_margin,
        },
        {
            "Strategic Scenario": "3. Aggressive Case",
            "Discount Cap": "15.0%",
            "Table Surcharge": "$25 / Unit",
            "International Model": "Bonded 3PL Master Distributor",
            "Churn Attrition": "3.0%",
            "Repriced Orders": res_aggr["affected_orders_count"],
            "Projected Operating EBITDA": aggr_profit,
            "Net EBITDA Uplift": aggr_uplift,
            "EBITDA Uplift (%)": aggr_pct_uplift,
            "Projected Operating Margin": aggr_margin,
        },
    ]

    return pd.DataFrame(scenarios)

