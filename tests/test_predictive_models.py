"""Unit tests for the predictive layer: sales forecast, discount response, churn risk."""
import pytest

from src.services.data_loader import load_sales_data


@pytest.fixture(scope="module")
def global_df():
    """Load the full 51,290 record Global Superstore dataset."""
    return load_sales_data()


def test_forecast_backtest_and_totals(global_df):
    """Forecast: holdout-validated candidate selection, sane interval, FY2015 total near the historical trajectory."""
    from src.services.predictive import forecast_monthly_sales

    fc = forecast_monthly_sales(global_df)
    assert "error" not in fc

    # The seasonal-naive benchmark must win the holdout on this ledger (measured: 10% vs ~17%)
    assert fc["model_used"].startswith("A:")
    assert 5.0 <= fc["backtest_mape_pct"] <= 15.0
    assert abs(fc["backtest_bias_pct"]) <= 5.0
    assert (
        fc["candidate_metrics"]["B: Damped log-linear trend"]["mape_pct"]
        > fc["candidate_metrics"]["A: Seasonal naive with drift"]["mape_pct"]
    )

    f = fc["forecast"]
    assert len(f) == 12
    assert (f["forecast"] > 0).all()
    assert (f["lower_80"] <= f["forecast"]).all()
    assert (f["forecast"] <= f["upper_80"]).all()

    # FY2015 continues the ~23% trajectory the deck documents
    assert 5_000_000 <= fc["forecast_fy_total"] <= 5_600_000
    assert 15.0 <= fc["fy_growth_pct"] <= 30.0


def test_discount_response_curve_and_retention(global_df):
    """Discount response: peak between 30-40%, 20% cap ~volume-neutral, all lines modelled."""
    from src.services.predictive import analyze_discount_response

    dr = analyze_discount_response(global_df)
    assert dr["n_lines"] == 51_290
    assert dr["holdout_mae_log"] < 0.6

    curve = {round(c["discount"], 2): c["volume_index"] for c in dr["curve"]}
    assert len(curve) == 8
    assert curve[0.0] == pytest.approx(100.0, abs=0.01)
    # Volume rises with shallow discounts, then declines past the interior peak
    assert curve[0.2] > curve[0.0]
    assert curve[0.7] < curve[0.3]

    retention = {round(r["cap"], 2): r for r in dr["retention"]}
    assert retention[0.20]["affected_lines"] == 11_328
    # Capping at 20% is predicted to be volume-neutral (measured ~101%; assumed churn says 95%)
    assert retention[0.20]["retained_pct"] == pytest.approx(100.0, abs=3.0)


def test_churn_model_valid(global_df):
    """Churn scoring: probabilities bounded, better-than-chance AUC, plausible lapse rate."""
    from src.services.predictive import score_customer_churn_risk

    cr = score_customer_churn_risk(global_df)
    assert "error" not in cr
    assert cr["n_customers"] == 1_575
    assert cr["auc_test"] > 0.65
    assert 3.0 <= cr["lapse_rate_pct"] <= 10.0

    scores = cr["customer_scores"]
    assert ((scores["p_lapse"] >= 0.0) & (scores["p_lapse"] <= 1.0)).all()
    assert set(["n_orders", "recency_days", "avg_discount", "share_lines_over_20pct"]).issubset(scores.columns)
    # Effects table covers every model feature
    assert len(cr["feature_effects"]) == 6


def test_predictive_charts_build(global_df):
    """The three Section 5 exhibits construct with the expected traces and labels."""
    from src.components.predictive_charts import (
        create_churn_lift_chart,
        create_discount_response_chart,
        create_sales_forecast_chart,
    )
    from src.services.predictive import (
        analyze_discount_response,
        forecast_monthly_sales,
        score_customer_churn_risk,
    )

    fc = forecast_monthly_sales(global_df)
    fig_fc = create_sales_forecast_chart(fc)
    names = [t.name for t in fig_fc.data]
    assert "Actual sales (FY2011-FY2014)" in names
    assert fc["model_used"] in " ".join(n for n in names if n)

    fig_dr = create_discount_response_chart(analyze_discount_response(global_df))
    assert any(getattr(s, "x0", None) == 20.0 for s in fig_dr.layout.shapes)  # 20% cap marker

    fig_ch = create_churn_lift_chart(score_customer_churn_risk(global_df))
    assert len(fig_ch.data[0].x) == 10  # one bar per risk decile
    assert "lapse rate" in fig_ch.data[0].name.lower()

