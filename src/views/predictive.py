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
        "If the current trajectory holds, FY2015 lands at $5.28M (+22.8%) - the fix does not need heroic growth. "
        "The 20% cap is measured to be volume-neutral, and the customers most likely to lapse can be named today, "
        "with the revenue riding on them.",
        "The Appendix - verify every number line by line",
    )
    st.markdown("## Chapter 5 - What Happens Next: FY2015 and the Customers to Save")
    st.markdown(
        "**The claim this chapter defends**: the strategy is robust to the future, not just fitted to the past. "
        "Three validated models - a backtested revenue forecast, a controlled discount-response regression, and "
        "a customer churn score - pressure-test the plan and point retention effort where it matters. Every "
        "model is scored on data it never saw during training."
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
                    "80% prediction interval. Two candidate models competed on a holdout year; the winner "
                    "(seasonal naive with drift) simply carries each month's latest level forward at the "
                    "training-window growth rate."
                ),
                key_takeaway=(
                    f"FY2015 revenue is forecast at ${fc['forecast_fy_total']/1e6:,.2f}M ({fc['fy_growth_pct']:+.1f}% vs "
                    "FY2014), with the usual Q4 peak above $600K. The trend-extrapolation benchmark over-predicted "
                    "the holdout year by double digits, so the validated simple model was preferred."
                ),
                business_impact=(
                    "The revival plan does not depend on heroic growth: even at the historical ~23% trajectory, "
                    "FY2015 revenue covers the $1.23M profit recovery with margin to spare."
                ),
                recommendation=(
                    "Re-fit this model every quarter as new months close; treat the 80% band as the planning "
                    "envelope for inventory and freight capacity."
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
            title="The Ledger Shows Deep Discounts Do Not Buy Proportional Volume",
            what_it_shows=(
                "A controlled regression of line volume on discount depth, holding product category, market, year, "
                "and month fixed (Q4 seasonality is the big confounder - December discounts coincide with "
                "high demand, not because of the discount)."
            ),
            key_takeaway=(
                "Predicted volume peaks around a 30-40% discount and *declines* beyond it: the 60-70% discounts in "
                "Turkey and Nigeria bought less volume than a 20% discount would. Capping every line at 20% is "
                "predicted to retain about "
                f"{r20['retained_pct']:.0f}% of volume - the data-driven replacement for the simulator's assumed 5% churn."
            ),
            business_impact=(
                "This is the strongest evidence yet for the discount cap: the volume we fear losing from capping "
                "is, on this ledger, already smaller than the volume deep discounts fail to attract."
            ),
            recommendation=(
                "Use the measured retention (not the assumed churn) when re-running the Chapter 4 simulator; "
                "treat the 15% aggressive-cap case as approximately volume-neutral too."
            ),
        )
        st.caption(
            "Caveat: this is observational data, not an experiment. Discounts were handed out non-randomly, so the "
            "curve measures association under controls - strong enough to bound the churn assumption, not proof of "
            "causation."
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
            high_risk = scores[scores["risk_tier"] == "High (50%+)"]
            m1, m2, m3 = st.columns(3)
            m1.metric("Model AUC (holdout)", f"{cr['auc_test']:.2f}", "0.50 = coin flip")
            m2.metric("Customers scored", f"{cr['n_customers']:,}")
            m3.metric(
                "Revenue at high risk",
                f"${high_risk['pre_sales'].sum()/1e3:,.0f}K",
                f"{len(high_risk):,} customers at 50%+ lapse probability",
            )

            render_chart_story_card(
                title="One in Five High-Risk Customers Can Be Named Today",
                what_it_shows=(
                    "Customers sorted into ten deciles by predicted lapse probability. A customer 'lapses' if they "
                    "place no order in the year after the feature window closes; features use only pre-2014 "
                    "behaviour (order recency, frequency, average discount, deep-discount share, order value), so "
                    "the score is a genuine prediction, not a restatement of the label."
                ),
                key_takeaway=(
                    f"The model separates lapsers from stayers at AUC {cr['auc_test']:.2f} on held-out customers, "
                    "and the top deciles lapse at many times the average rate. Deep-discount exposure is a "
                    "positive churn driver - customers acquired on 20%+ discounts are the least loyal."
                ),
                business_impact=(
                    "Retention effort can be targeted: the high-risk tier holds the revenue most likely to vanish "
                    "when the 20% cap lands, tightening the churn allowance in the turnaround plan."
                ),
                recommendation=(
                    "Assign account managers to the high-risk tier before the discount cap goes live; monitor "
                    "whether their repeat-purchase rate closes the gap to the average."
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
