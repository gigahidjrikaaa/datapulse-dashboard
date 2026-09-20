"""Unit tests for the analyzer service with Global Superstore analytical tasks."""

import pandas as pd
import pytest

from src.services.analyzer import (
    analyze_discount_impact,
    analyze_geographic_drilldown,
    analyze_product_breakdown,
    compute_overview_kpis,
    compute_quarterly_seasonality,
    compute_scenario_sensitivity_matrix,
    compute_territory_quadrant_matrix,
    compute_yoy_growth,
    filter_data,
    simulate_turnaround_impact,
)


@pytest.fixture
def sample_superstore_df() -> pd.DataFrame:
    """Fixture providing mock Global Superstore DataFrame."""
    return pd.DataFrame(
        {
            "Row ID": [1, 2, 3, 4],
            "Order ID": ["O1", "O2", "O3", "O4"],
            "Order Date": pd.to_datetime(["2011-05-01", "2012-06-01", "2013-07-01", "2014-08-01"]),
            "Year": [2011, 2012, 2013, 2014],
            "Market": ["US", "EU", "EMEA", "LATAM"],
            "Region": ["West", "Central", "Middle East", "South"],
            "Country": ["United States", "Germany", "Turkey", "Brazil"],
            "Category": ["Technology", "Furniture", "Furniture", "Office Supplies"],
            "Sub-Category": ["Phones", "Chairs", "Tables", "Paper"],
            "Segment": ["Consumer", "Corporate", "Consumer", "Home Office"],
            "Sales": [1000.0, 500.0, 400.0, 100.0],
            "Profit": [200.0, 50.0, -150.0, 25.0],
            "Discount": [0.0, 0.1, 0.6, 0.0],
            "Discount_Bucket": pd.Categorical(
                ["0%", "0.1-10%", ">50%", "0%"],
                categories=["0%", "0.1-10%", "10.1-20%", "20.1-30%", "30.1-40%", "40.1-50%", ">50%"],
            ),
            "Quantity": [2, 1, 4, 5],
            "Shipping Cost": [20.0, 15.0, 30.0, 5.0],
        }
    )


def test_compute_overview_kpis(sample_superstore_df: pd.DataFrame) -> None:
    """Verify overview KPIs computation for Global Superstore."""
    kpis = compute_overview_kpis(sample_superstore_df)
    # Total sales: 1000 + 500 + 400 + 100 = 2000
    assert kpis["total_sales"] == pytest.approx(2000.0)
    # Total profit: 200 + 50 - 150 + 25 = 125
    assert kpis["total_profit"] == pytest.approx(125.0)
    # Margin: 125 / 2000 * 100 = 6.25%
    assert kpis["profit_margin"] == pytest.approx(6.25)
    # Loss drag: abs(-150) = 150
    assert kpis["profit_loss_drag"] == pytest.approx(150.0)
    # Loss count: 1 order out of 4 = 25%
    assert kpis["loss_order_count"] == 1.0
    assert kpis["loss_order_pct"] == pytest.approx(25.0)


def test_compute_yoy_growth(sample_superstore_df: pd.DataFrame) -> None:
    """Verify YoY calculations across years."""
    yoy = compute_yoy_growth(sample_superstore_df)
    assert len(yoy) == 4
    assert list(yoy["Year"]) == [2011, 2012, 2013, 2014]
    assert "Sales_YoY_Growth" in yoy.columns
    assert "Profit_Margin" in yoy.columns


def test_analyze_discount_impact(sample_superstore_df: pd.DataFrame) -> None:
    """Verify discount bucket aggregation highlights loss tiers."""
    disc_summary = analyze_discount_impact(sample_superstore_df)
    assert not disc_summary.empty
    high_disc = disc_summary[disc_summary["Discount_Bucket"] == ">50%"]
    assert not high_disc.empty
    assert high_disc["Total_Profit"].iloc[0] < 0


def test_analyze_geographic_drilldown(sample_superstore_df: pd.DataFrame) -> None:
    """Verify country-level loss identification."""
    mkt, reg, country = analyze_geographic_drilldown(sample_superstore_df)
    assert not country.empty
    turkey_row = country[country["Country"] == "Turkey"].iloc[0]
    assert turkey_row["Profit"] == -150.0


def test_analyze_product_breakdown(sample_superstore_df: pd.DataFrame) -> None:
    """Verify Sub-Category aggregation identifies Tables as loss-maker."""
    cat, subcat = analyze_product_breakdown(sample_superstore_df)
    assert not subcat.empty
    tables_row = subcat[subcat["Sub-Category"] == "Tables"].iloc[0]
    assert tables_row["Profit"] == -150.0


def test_filter_data(sample_superstore_df: pd.DataFrame) -> None:
    """Test multi-dimensional filtering."""
    filtered = filter_data(sample_superstore_df, markets=["US", "EU"])
    assert len(filtered) == 2
    assert set(filtered["Market"]) == {"US", "EU"}


def test_compute_territory_quadrant_matrix(sample_superstore_df: pd.DataFrame) -> None:
    """Verify strategic portfolio quadrant categorization of sovereign territories."""
    quad_df = compute_territory_quadrant_matrix(sample_superstore_df)
    assert not quad_df.empty
    assert "Portfolio_Quadrant" in quad_df.columns
    assert "Operating_Margin" in quad_df.columns
    assert "Profit_Margin" in quad_df.columns

    # Turkey has negative profit, must be categorized as Deficit Rationalization Priority
    turkey_row = quad_df[quad_df["Country"] == "Turkey"].iloc[0]
    assert turkey_row["Portfolio_Quadrant"] == "Deficit Rationalization Priority"

    # United States has top sales and 20% margin, must be Core Value Engine
    us_row = quad_df[quad_df["Country"] == "United States"].iloc[0]
    assert us_row["Portfolio_Quadrant"] == "Core Value Engine"


def test_simulate_turnaround_impact(sample_superstore_df: pd.DataFrame) -> None:
    """Verify financial turnaround simulation engine and EBITDA bridge arithmetic."""
    sim = simulate_turnaround_impact(
        df=sample_superstore_df,
        max_discount_cap=0.20,
        restructure_deficit_territories=True,
        table_freight_surcharge=15.0,
        volume_attrition_rate=0.05,
    )

    assert sim["baseline_profit"] == pytest.approx(125.0)
    assert sim["affected_orders_count"] == 1  # Only O3 had discount 0.60 > 0.20
    assert sim["pricing_recovery"] > 0.0
    assert sim["territory_recovery"] == pytest.approx(150.0)  # Turkey loss (-150) recovered
    assert sim["table_freight_recovery"] == pytest.approx(4 * 15.0)  # 4 Table units * $15 = $60
    assert sim["attrition_drag"] > 0.0

    # Test mathematical consistency of the EBITDA waterfall bridge
    expected_profit = (
        sim["baseline_profit"]
        + sim["pricing_recovery"]
        + sim["territory_recovery"]
        + sim["table_freight_recovery"]
        - sim["attrition_drag"]
    )
    assert sim["projected_profit"] == pytest.approx(expected_profit)
    assert sim["net_ebitda_uplift"] == pytest.approx(expected_profit - sim["baseline_profit"])

    # Test empty dataframe behavior
    empty_sim = simulate_turnaround_impact(pd.DataFrame())
    assert empty_sim["baseline_profit"] == 0.0
    assert empty_sim["net_ebitda_uplift"] == 0.0


def test_compute_quarterly_seasonality(sample_superstore_df: pd.DataFrame) -> None:
    """Verify quarterly seasonality aggregation and revenue share calculation."""
    q_df = compute_quarterly_seasonality(sample_superstore_df)
    assert not q_df.empty
    assert "Quarter_Num" in q_df.columns
    assert "Quarter_Share_Pct" in q_df.columns
    assert "Sales" in q_df.columns
    assert "Profit" in q_df.columns

    # Test empty DataFrame
    assert compute_quarterly_seasonality(pd.DataFrame()).empty


def test_compute_scenario_sensitivity_matrix(sample_superstore_df: pd.DataFrame) -> None:
    """Verify pre-computed scenario sensitivity matrix generation."""
    matrix = compute_scenario_sensitivity_matrix(sample_superstore_df)
    assert not matrix.empty
    assert len(matrix) == 4  # Baseline + 3 Turnaround Cases
    scenarios = list(matrix["Strategic Scenario"])
    assert "Baseline (Status Quo)" in scenarios
    assert "1. Conservative Case" in scenarios
    assert "2. Base Case (Recommended Plan)" in scenarios
    assert "3. Aggressive Case" in scenarios

    assert "Projected Operating EBITDA" in matrix.columns
    assert "Net EBITDA Uplift" in matrix.columns
    assert "Projected Operating Margin" in matrix.columns

    # Test empty DataFrame
    assert compute_scenario_sensitivity_matrix(pd.DataFrame()).empty

