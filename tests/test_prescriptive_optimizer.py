"""Unit tests for the prescriptive layer: measured-response simulator and policy optimizer."""
import pytest

from src.services.data_loader import load_sales_data


@pytest.fixture(scope="module")
def global_df():
    """Load the full 51,290 record Global Superstore dataset."""
    return load_sales_data()


def test_measured_simulator_reconciles_with_legacy_base_case(global_df):
    """At the base-case levers, the measured simulator lands near the legacy $2.70M/19.9% result
    - no assumed churn, no arbitrary drag factor."""
    from src.services.prescriptive import simulate_turnaround_measured

    sim = simulate_turnaround_measured(global_df, discount_cap=0.20, table_freight_surcharge=15.0)
    assert sim["attrition_drag"] == 0.0
    assert sim["volume_ratio"] == pytest.approx(1.013, abs=0.005)
    assert sim["pricing_recovery"] == pytest.approx(1_035_263, abs=1_500)
    assert sim["territory_recovery"] == pytest.approx(179_197.95, abs=1.0)
    assert sim["table_freight_recovery"] == pytest.approx(46_245.0, abs=1.0)
    assert sim["projected_profit"] == pytest.approx(2_728_163, abs=2_000)
    assert sim["projected_margin"] == pytest.approx(19.9, abs=0.2)


def test_policy_optimizer_grid_and_best(global_df):
    """Optimizer: full grid searched, best row is the max, optimum uses the measured response."""
    from src.services.prescriptive import optimize_turnaround_policy

    opt = optimize_turnaround_policy(global_df)
    assert opt["n_policies"] == 30  # 5 caps x 6 surcharges
    assert len(opt["grid"]) == opt["n_policies"]
    assert opt["grid"]["Projected operating profit"].max() == pytest.approx(opt["best"]["Projected operating profit"], abs=0.01)

    # Measured retention is near volume-neutral across the policy range (96%-104%)
    for cap, ratio in opt["retention_by_cap"].items():
        assert 0.90 <= ratio <= 1.10
    assert opt["retention_by_cap"][0.20] == pytest.approx(1.013, abs=0.005)

    # Every policy beats the status-quo baseline
    assert (opt["grid"]["Projected operating profit"] > opt["baseline_profit"]).all()
    # The optimum rides on the tightest cap the grid offers (measured response is near-flat)
    assert opt["best"]["cap_value"] == pytest.approx(0.10, abs=1e-9)


def test_best_cap_by_market_table(global_df):
    """Per-market tuner: one row per market, best caps within the grid, Canada has no capped lines."""
    from src.services.prescriptive import best_cap_by_market

    markets = best_cap_by_market(global_df)
    assert len(markets) == 7
    assert set(markets["Best cap"]).issubset({"10%", "15%", "20%", "25%", "30%"})
    canada = markets[markets["Market"] == "Canada"].iloc[0]
    assert canada["Uplift from tuning (vs global 20%)"] == pytest.approx(0.0, abs=1.0)
    assert (markets["Profit at best cap"] >= markets["Profit at global 20% cap"] - 1.0).all()


def test_profit_surface_chart_builds(global_df):
    """The policy-surface heatmap renders one cell per policy with the optimum in the title."""
    from src.components.predictive_charts import create_policy_profit_surface_chart
    from src.services.prescriptive import optimize_turnaround_policy

    opt = optimize_turnaround_policy(global_df)
    fig = create_policy_profit_surface_chart(opt["grid"], opt["best"])
    assert len(fig.data) == 1
    assert fig.data[0].type == "heatmap"
    assert len(fig.data[0].z) == 5 and len(fig.data[0].z[0]) == 6
    assert "10%" in fig.layout.title.text and "$25" in fig.layout.title.text
