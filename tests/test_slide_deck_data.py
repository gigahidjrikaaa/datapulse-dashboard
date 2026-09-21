"""Unit test suite verifying presentation slide deck data points against dataset."""
import pytest
import os
from src.services.data_loader import load_sales_data
from src.services.analyzer import (
    compute_overview_kpis,
    compute_yoy_growth,
    simulate_turnaround_impact,
)


@pytest.fixture(scope="module")
def global_df():
    """Load the full 51,290 record Global Superstore dataset."""
    return load_sales_data()


def test_slide2_and_3_topline_growth(global_df):
    """Slide 2 & 3: Revenue scaled from $2.26M to $4.30M (+90.3%, CAGR: 23.9%)."""
    yoy = compute_yoy_growth(global_df)
    sales_2011 = yoy.loc[yoy["Year"] == 2011, "Sales"].values[0]
    sales_2014 = yoy.loc[yoy["Year"] == 2014, "Sales"].values[0]
    growth_pct = (sales_2014 - sales_2011) / sales_2011 * 100.0
    cagr = ((sales_2014 / sales_2011) ** (1 / 3) - 1) * 100.0

    assert sales_2011 == pytest.approx(2_259_450.90, rel=1e-3)
    assert sales_2014 == pytest.approx(4_299_865.87, rel=1e-3)
    assert growth_pct == pytest.approx(90.3, abs=0.1)
    assert cagr == pytest.approx(23.9, abs=0.1)


def test_slide2_and_5_profit_leakage(global_df):
    """Slide 2 & 5: $920,646 profit destroyed across 12,544 loss-making lines (24.5%)."""
    kpis = compute_overview_kpis(global_df)
    assert kpis["loss_order_count"] == 12544
    assert kpis["loss_order_pct"] == pytest.approx(24.46, abs=0.1)
    assert kpis["profit_loss_drag"] == pytest.approx(920_646.16, abs=1.0)
    assert kpis["profitable_order_gain"] == pytest.approx(2_388_103.45, abs=1.0)
    assert kpis["total_profit"] == pytest.approx(1_467_457.29, abs=1.0)


def test_slide6_country_deficits(global_df):
    """Slide 6: Turkey (-$98K) and Nigeria (-$81K) lead sovereign deficits."""
    turkey_profit = global_df[global_df["Country"] == "Turkey"]["Profit"].sum()
    nigeria_profit = global_df[global_df["Country"] == "Nigeria"]["Profit"].sum()
    netherlands_profit = global_df[global_df["Country"] == "Netherlands"]["Profit"].sum()
    honduras_profit = global_df[global_df["Country"] == "Honduras"]["Profit"].sum()

    assert turkey_profit == pytest.approx(-98_447.23, abs=1.0)
    assert nigeria_profit == pytest.approx(-80_750.72, abs=1.0)
    assert netherlands_profit == pytest.approx(-41_070.08, abs=1.0)
    assert honduras_profit == pytest.approx(-29_482.37, abs=1.0)
    assert (turkey_profit + nigeria_profit) == pytest.approx(-179_197.95, abs=1.0)


def test_slide7_tables_anomaly(global_df):
    """Slide 7: Tables is the sole net deficit sub-category (-$64.1K on $757K sales)."""
    sub_perf = global_df.groupby("Sub-Category")["Profit"].sum()
    deficit_subs = sub_perf[sub_perf < 0]
    assert len(deficit_subs) == 1
    assert "Tables" in deficit_subs.index
    assert deficit_subs["Tables"] == pytest.approx(-64_083.19, abs=1.0)


def test_slide8_discount_inversion(global_df):
    """Slide 8: Orders > 20% discount destroy $814,682 across 11,328 lines."""
    over_20 = global_df[global_df["Discount"] > 0.20]
    assert len(over_20) == 11328
    assert over_20["Profit"].sum() == pytest.approx(-814_682.09, abs=1.0)


def test_slide12_and_13_base_case_turnaround(global_df):
    """Slide 12 & 13: Base Case turnaround simulation lifts EBITDA +$1.23M to $2.70M (19.9% margin)."""
    sim = simulate_turnaround_impact(
        global_df,
        max_discount_cap=0.20,
        restructure_deficit_territories=True,
        table_freight_surcharge=15.0,
        volume_attrition_rate=0.05,
    )
    assert sim["baseline_profit"] == pytest.approx(1_467_457.29, abs=1.0)
    assert sim["pricing_recovery"] == pytest.approx(1_032_488.44, abs=1.0)
    assert sim["territory_recovery"] == pytest.approx(179_197.95, abs=1.0)
    assert sim["table_freight_recovery"] == pytest.approx(46_245.00, abs=1.0)
    assert sim["attrition_drag"] == pytest.approx(24_127.63, abs=1.0)
    assert sim["net_ebitda_uplift"] == pytest.approx(1_233_803.75, abs=1.0)
    assert sim["projected_profit"] == pytest.approx(2_701_261.04, abs=1.0)
    assert sim["projected_margin"] == pytest.approx(19.89, abs=0.1)


def test_html_slide_no_typo_symbol():
    """Verify HTML slide deck does not contain '$-' currency formatting error."""
    html_path = os.path.join("presentation", "board_deck.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "$-64K" not in content, "Found '$-64K' typo in board_deck.html"
        assert "-$64K" in content, "Expected '-$64K' in board_deck.html"


def test_slide2_operating_profit_visual_and_legend():
    """Verify Slide 2 includes Operating Profit visual points, legend, and volume card."""
    html_path = os.path.join("presentation", "board_deck.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "$249K" in content
    assert "$504K" in content
    assert "Operating profit (line)" in content
    assert "Order volume (+92.1%)" in content
    assert "Avg order value (flat, -0.9%)" in content


def test_slide7_and_8_legends_and_colors():
    """Verify Slide 7 has discount margin legend and Slide 8 uses var(--rule) matching legend."""
    html_path = os.path.join("presentation", "board_deck.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Profitable margin (&le;20% discount)" in content
    assert "Operating deficit (&gt;20% discount)" in content
    # In slide 8, Same Day and First Class should have fill="var(--rule)"
    assert 'fill="var(--rule)"/><text class="sv-val" x="717" y="220" text-anchor="start">17.4%</text>' in content


def test_dashboard_priority_chart_and_discount_cliff_legend(global_df):
    """Verify create_priority_freight_chart and create_discount_cliff_chart have traces with legends."""
    from src.services.analyzer import analyze_discount_impact, analyze_shipping_and_priority
    from src.components.charts import create_discount_cliff_chart, create_priority_freight_chart

    disc_df = analyze_discount_impact(global_df)
    cliff_fig = create_discount_cliff_chart(disc_df)
    assert len(cliff_fig.data) == 2
    assert "Profitable Tier" in cliff_fig.data[0].name
    assert "Deficit Tier" in cliff_fig.data[1].name

    _, priority_df = analyze_shipping_and_priority(global_df)
    priority_fig = create_priority_freight_chart(priority_df)
    assert len(priority_fig.data) == 2 # Bar and line
    assert "Freight Cost Ratio (%)" in priority_fig.data[0].name
    assert "Avg Shipping Cost ($)" in priority_fig.data[1].name
