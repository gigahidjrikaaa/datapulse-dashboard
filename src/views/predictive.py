"""Chapter 5 View: What Happens Next — FY2015 forecast, discount response, churn risk.

Models run on the full FY2011-FY2014 ledger (st.session_state raw data), not the sidebar
filters: time-series and customer-level models need the complete continuous history.
"""

import pandas as pd
import streamlit as st

from src.components.narratives import render_chart_story_card, render_data_dictionary_expander
from src.components.predictive_charts import (
    create_churn_lift_chart,
    create_discount_response_chart,
    create_sales_forecast_chart,
)
from src.components.story import render_story_ribbon
from src.services.predictive import (
    analyze_discount_response,
    forecast_monthly_sales,
    score_customer_churn_risk,
)


@st.cache_data(show_spinner="Fitting forecast model...")
def _cached_forecast(df: pd.DataFrame) -> dict:
    return forecast_monthly_sales(df)


@st.cache_data(show_spinner="Estimating discount response...")
def _cached_discount_response(df: pd.DataFrame) -> dict:
    return analyze_discount_response(df)


@st.cache_data(show_spinner="Scoring customer churn risk...")
def _cached_churn(df: pd.DataFrame) -> dict:
    return score_customer_churn_risk(df)


def render_predictive_view(df: pd.DataFrame) -> None:
    """Render Chapter 5: predictive models with holdout validation."""
    render_story_ribbon(
        "ch5",
        "If current trends continue, FY2015 revenue lands at $5.28M (+22.8%). The 20% cap barely changes "
        "demand, and we can name the customers most likely to stop ordering - and how much they spend.",
        "The Appendix - verify every number line by line",
    )
    st.markdown("## Chapter 5 - What Happens Next: FY2015 and the Customers to Save")
    st.markdown(
        "**What this chapter shows**: three simple models, each tested on data it never saw during training. "
        "They answer three questions: what will sales do in 2015, what happens to demand when discounts are "
        "capped, and which customers are about to leave. Models run on the full FY2011-FY2014 ledger; sidebar "
        "filters do not apply."
    )
    st.markdown("---")

    with st.container(border=True):
        st.markdown("### The Core Question: What Will Happen Next?")
        st.markdown(
            """
            **What we're predicting**:
            Chapters 1-4 explained *what happened* and *why*. This chapter predicts *what happens next*:

            1. **Revenue**: What will monthly sales look like in FY2015 if the current trajectory holds?
            2. **Demand response**: If discounts are capped at 20%, how much volume would we actually lose?
            3. **Customers**: Which customers are most likely to lapse next year, and what revenue rides on them?
            """
        )

    render_data_dictionary_expander()

    if df is None or df.empty:
        st.warning("No data available for the predictive models.")
        return

    # Predictive models need the complete continuous history - run on the full ledger,
    # not the sidebar-filtered slice
    raw_df = st.session_state.get("raw_df", df)
    if raw_df is None or raw_df.empty:
        raw_df = df

    # ------------------------------------------------------------------
    # Model 1: FY2015 sales forecast
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("### 1. FY2015 Revenue Forecast (Validated on a Holdout Year)")
        fc = _cached_forecast(raw_df)
        if "error" in fc:
            st.warning(fc["error"])
        else:
            st.plotly_chart(create_sales_forecast_chart(fc), width="stretch")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("FY2015 Forecast", f"${fc['forecast_fy_total']/1e6:,.2f}M")
            m2.metric(
                "Growth vs FY2014",
                f"{fc['fy_growth_pct']:+.1f}%",
                f"FY2014 actual: ${fc['last_actual_fy_total']/1e6:,.2f}M",
            )
            m3.metric("Backtest Error (MAPE)", f"{fc['backtest_mape_pct']:.1f}%", "lower is better", delta_color="inverse")
            m4.metric("Implied Annual Drift", f"{(fc['drift'] - 1) * 100:+.1f}%", "training-window growth")

            candidate_md = "\n".join(
                f"| {name} | {m['mape_pct']:.1f}% | {m['bias_pct']:+.1f}% |"
                for name, m in fc["candidate_metrics"].items()
            )
            st.markdown(
                "**How the model was chosen**: both candidates were trained on FY2011-FY2013 and scored on FY2014 "
                "(never seen during training). The lower-error candidate produced the forecast.\n\n"
                "| Candidate | Backtest MAPE | Backtest bias |\n"
                "| :--- | :--- | :--- |\n"
                f"{candidate_md}"
            )

            render_chart_story_card(
                title="FY2015 Sales Are Tracking Toward $5.3M If Trends Hold",
                what_it_shows=(
                    "48 months of actual monthly sales (blue) and the 12-month FY2015 forecast (dashed) with an "
                    "80% prediction band. Two models were tested on a year they had never seen; the winner "
                    "repeats last year's pattern with the measured growth rate added on top - and it beat the "
                    "fancier trend model."
                ),
                key_takeaway=(
                    f"FY2015 revenue is forecast at ${fc['forecast_fy_total']/1e6:,.2f}M ({fc['fy_growth_pct']:+.1f}% vs "
                    "FY2014), with the usual Q4 peak above $600K. The trend model over-predicted the holdout "
                    "year, so the simple model that passed the test makes the forecast."
                ),
                business_impact=(
                    "The plan does not depend on fast growth: at the usual ~23% pace, FY2015 revenue comfortably "
                    "covers the $1.23M profit recovery."
                ),
                recommendation=(
                    "Re-fit this model every quarter as new months close; treat the 80% band as the planning "
                    "range for inventory and freight capacity."
                ),
            )

    st.divider()

    # ------------------------------------------------------------------
    # Model 2: Discount-demand response
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("### 2. Measured Demand Response to Discounts (What a 20% Cap Really Costs)")
        dr = _cached_discount_response(raw_df)
        st.plotly_chart(create_discount_response_chart(dr), width="stretch")

        r20 = next(r for r in dr["retention"] if r["cap"] == 0.20)
        r15 = next(r for r in dr["retention"] if r["cap"] == 0.15)
        m1, m2, m3 = st.columns(3)
        m1.metric("Volume retained @ 20% cap", f"{r20['retained_pct']:.1f}%", f"across {r20['affected_lines']:,} lines")
        m2.metric("Volume retained @ 15% cap", f"{r15['retained_pct']:.1f}%", f"across {r15['affected_lines']:,} lines")
        m3.metric("Holdout error (log MAE)", f"{dr['holdout_mae_log']:.2f}", f"{dr['n_lines']:,} lines modelled")

        render_chart_story_card(
            title="Deep Discounts Do Not Buy Much Extra Volume",
            what_it_shows=(
                "A regression of order volume on discount depth, controlling for product, market, year, and "
                "month. The month control matters: December has both big discounts and big sales, and the model "
                "separates the two."
            ),
            key_takeaway=(
                "Predicted volume peaks around a 30-40% discount and falls after that: the 60-70% discounts in "
                "Turkey and Nigeria brought in less volume than a 20% discount would. Capping at 20% keeps about "
                f"{r20['retained_pct']:.0f}% of volume, so the simulator no longer needs the 5% churn guess."
            ),
            business_impact=(
                "This is the strongest evidence yet for the discount cap: the volume we fear losing from capping "
                "is smaller than the volume the deep discounts never attracted in the first place."
            ),
            recommendation=(
                "Use this measured volume effect (not the 5% guess) when running the Chapter 4 simulator; the "
                "15% cap case is close to volume-neutral too."
            ),
        )
        st.caption(
            "Note: this is historical data, not an experiment. The curve shows what happened together, not "
            "proof of cause and effect. It is good enough to check the churn guess, not to promise exact numbers."
        )

    st.divider()

    # ------------------------------------------------------------------
    # Model 3: Customer churn risk
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("### 3. Customer Churn Risk Scoring (Who Is Likely to Lapse?)")
        cr = _cached_churn(raw_df)
        if "error" in cr:
            st.warning(cr["error"])
        else:
            st.plotly_chart(create_churn_lift_chart(cr), width="stretch")

            scores = cr["customer_scores"]
            high_risk = scores[scores["risk_tier"] == "High (top third)"]
            top_decile = scores.nlargest(max(len(scores) // 10, 1), "p_lapse")
            top_lift = top_decile["lapsed"].mean() / max(cr["lapse_rate_pct"] / 100.0, 1e-9)
            m1, m2, m3 = st.columns(3)
            m1.metric("Model AUC (holdout)", f"{cr['auc_test']:.2f}", "0.50 = coin flip")
            m2.metric("Customers scored", f"{cr['n_customers']:,}")
            m3.metric(
                "Revenue in the top risk third",
                f"${high_risk['pre_sales'].sum()/1e3:,.0f}K",
                f"lapsing {top_lift:.1f}x the average rate",
            )

            render_chart_story_card(
                title="The Model Flags the Customers Most Likely to Leave",
                what_it_shows=(
                    "Customers sorted into ten groups by predicted chance of lapsing. A customer counts as "
                    "'lapsed' if they placed no order in 2014. The score uses only pre-2014 behaviour - how "
                    "recently and how often they ordered, their average discount, how much of what they bought "
                    "was discounted over 20%, and their order value - so it is a real prediction."
                ),
                key_takeaway=(
                    f"On held-out customers the model reaches AUC {cr['auc_test']:.2f} (0.50 would be a coin "
                    "flip), and the top groups lapse at several times the average rate. Heavy discount exposure "
                    "is a churn signal: customers trained on 20%+ discounts are the least loyal."
                ),
                business_impact=(
                    "Retention work can be targeted. The high-risk tier holds the revenue most likely to "
                    "disappear when the 20% cap lands, which tightens the churn estimate in the turnaround plan."
                ),
                recommendation=(
                    "Assign account managers to the high-risk tier before the discount cap goes live; watch "
                    "whether their repeat-purchase rate moves back toward the average."
                ),
            )

            top_risk = (
                high_risk.sort_values("pre_sales", ascending=False)
                .head(20)[["Customer ID", "n_orders", "recency_days", "avg_discount", "share_lines_over_20pct", "pre_sales", "p_lapse"]]
                .rename(
                    columns={
                        "n_orders": "Orders (pre-2014)",
                        "recency_days": "Days since last order",
                        "avg_discount": "Avg discount",
                        "share_lines_over_20pct": "Share of lines >20% off",
                        "pre_sales": "Revenue at stake",
                        "p_lapse": "P(lapse)",
                    }
                )
            )
            st.markdown("#### Top 20 High-Risk Customers by Revenue at Stake")
            st.dataframe(
                top_risk.style.format(
                    {
                        "Avg discount": "{:.1%}",
                        "Share of lines >20% off": "{:.1%}",
                        "Revenue at stake": "${:,.0f}",
                        "P(lapse)": "{:.2f}",
                    }
                ),
                width="stretch",
                hide_index=True,
            )

    st.divider()

    with st.expander("Methodology & Model Caveats", expanded=False):
        st.markdown(
            """
            **Forecast (Model 1)** - Two candidates trained on FY2011-FY2013 and scored on FY2014:
            a seasonal-naive-with-drift benchmark and a damped log-linear trend with month seasonality.
            The lower-MAPE candidate generates FY2015. The 80% interval comes from holdout residual quantiles
            (naive) or residual sigma (trend). Re-fit monthly as actuals close.

            **Discount response (Model 2)** - OLS of log quantity on discount and discount squared plus
            category, market, year, and month dummies across all 51,290 lines; validated on a random 20% holdout.
            Retention under a cap compares predicted quantity at the cap vs the actual discount for every
            affected line. Observational data: the curve is a controlled association, not a causal estimate.

            **Churn risk (Model 3)** - L2-regularised logistic regression (Newton-Raphson) scoring every
            customer active before 2014 on pre-2014 behaviour only; label = no order in 2014. Validated by AUC
            on a 25% customer holdout. Right-censoring applies: customers acquired in late 2013 have short
            observed histories, so treat individual scores as directional.
            """
        )
