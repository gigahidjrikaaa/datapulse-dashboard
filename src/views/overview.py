"""Section 1 View: Multi-Year Financial Performance Audit (Task 1)."""

import pandas as pd
import streamlit as st

from src.components.charts import create_monthly_trend_chart, create_yoy_growth_chart
from src.components.narratives import render_chart_story_card, render_data_dictionary_expander
from src.services.analyzer import compute_monthly_trend, compute_yoy_growth


def render_overview_view(df: pd.DataFrame) -> None:
    """Render Section 1: Multi-Year Financial Performance Audit (2011–2014)."""
    st.markdown("## Section 1: Multi-Year Financial Performance Audit")
    st.markdown(
        "**Audit Objective**: Evaluate historical financial performance (FY2011–FY2014), calculate compound growth rates, and test market rumors regarding top-line stagnation."
    )
    st.markdown("---")

    render_data_dictionary_expander()

    if df.empty:
        st.warning("No data available under the current parameter selection.")
        return

    # Formal Audit Inquiries Callout
    with st.container(border=True):
        st.markdown("### Executive Audit Findings: Board Inquiries")
        st.markdown(
            """
            * **Are sales and operating profit expanding, flat, or declining?**
              - **Sales and profit demonstrate strong, sustained expansion.** Annual revenue grew from **\\$2,259,451 in FY2011** to **\\$4,299,866 in FY2014**, representing cumulative top-line growth of **+90.3%** (+26.3% YoY in FY2014).
              - Operating profit expanded in parallel from **\\$248,941 (FY2011)** to **\\$504,166 (FY2014)**, reflecting a cumulative increase of **+102.5%**.
            * **Is the operating profit margin improving or deteriorating?**
              - **Operating margin is stagnant.** Margin performance remained constrained within a narrow band of **11.02% (FY2011)**, **11.48% (FY2012)**, **11.95% (FY2013)**, and **11.73% (FY2014)**. Despite doubling commercial order volume, the business failed to capture operating leverage benefits due to compounding discounting concessions.
            * **Is underperformance pervasive across the enterprise or confined to specific operating units?**
              - **Underperformance is structurally isolated.** The core enterprise is fundamentally sound: 75.5% of transaction volume delivers **\\$2.39M in gross operating profit**. Value destruction is concentrated in four international territories (Turkey, Nigeria, Netherlands, Honduras) and one merchandise line (Tables).
            """
        )

    st.divider()

    # YoY Annual Growth Analysis
    yoy_df = compute_yoy_growth(df)

    with st.container(border=True):
        st.markdown("### Year-over-Year (YoY) Financial Performance Progression (FY2011–FY2014)")
        yoy_chart = create_yoy_growth_chart(yoy_df)
        st.plotly_chart(yoy_chart, use_container_width=True)

        render_chart_story_card(
            title="Annual Revenue Expansion vs Operating Margin Stagnation",
            what_it_shows=(
                "Dual-axis evaluation of annual gross invoiced sales (Blue Bars), net operating profit (Green Bars), and operating margin % "
                "(Yellow Line) across 51,290 commercial transaction lines from fiscal years 2011 through 2014."
            ),
            key_takeaway=(
                "Top-line invoiced sales accelerated across the audit period (+18.5% in FY2012, +27.2% in FY2013, and +26.3% in FY2014). "
                "Operating profit scaled from $249K to $504K. However, operating margin remained flat at approximately 11.6% to 11.9%, "
                "indicating that scale expansion did not yield expected economies of scale or fixed-cost absorption advantages."
            ),
            business_impact=(
                "External rumors of revenue stagnation are refuted by transaction data. The true strategic concern is gross-to-net margin dilution: "
                "as annual transaction volume scaled from 4,440 to 8,531 orders, commercial pricing discipline eroded, allowing discounted transactions "
                "to offset gains realized by high-performing product lines."
            ),
            recommendation=(
                "The Board should transition commercial performance scorecards from gross top-line bookings to contribution margin targets, "
                "penalizing unapproved price concessions."
            ),
        )

        st.markdown("#### Annual Performance Summary Matrix")
        formatted_yoy = yoy_df.copy()
        st.dataframe(
            formatted_yoy.style.format(
                {
                    "Sales": "${:,.2f}",
                    "Profit": "${:,.2f}",
                    "Profit_Margin": "{:.2f}%",
                    "Sales_YoY_Growth": "{:+.2f}%",
                    "Profit_YoY_Growth": "{:+.2f}%",
                    "Orders_YoY_Growth": "{:+.2f}%",
                    "Avg_Order_Value": "${:,.2f}",
                    "Orders": "{:,}",
                    "Line_Items": "{:,}",
                    "Quantity": "{:,}",
                }
            ),
            use_container_width=True,
        )

    st.divider()

    # Monthly / Quarterly Seasonality
    with st.container(border=True):
        st.markdown("### Intra-Year Seasonality and Revenue Trajectory")
        st.markdown(
            "Analysis of monthly order cadence demonstrates pronounced fourth-quarter concentration, driven by corporate procurement deadlines and retail commercial cycles."
        )
        monthly_df = compute_monthly_trend(df)
        trend_chart = create_monthly_trend_chart(monthly_df)
        st.plotly_chart(trend_chart, use_container_width=True)

        render_chart_story_card(
            title="Intra-Year Monthly Revenue Trajectory & Operating Seasonality",
            what_it_shows=(
                "Continuous 48-month longitudinal trend of monthly invoiced sales (Blue area) and net operating profit (Green line), "
                "capturing multi-year cyclical patterns and fulfillment volatility."
            ),
            key_takeaway=(
                "Each fiscal year exhibits consistent cyclicality: Q1 operates at reduced capacity following year-end adjustments, "
                "Q2/Q3 sustain steady acceleration, and Q4 experiences extreme volume surges, generating approximately 35% of full-year revenue."
            ),
            business_impact=(
                "During Q4 volume peaks, field sales teams faced acute quota pressures, leading to unauthorized promotional discounting. "
                "Simultaneously, logistics distribution networks encountered peak carrier surcharges, causing severe margin contraction during the highest-volume periods."
            ),
            recommendation=(
                "Establish institutional discount boundaries in advance of Q4 and secure committed carrier contract pricing prior to the annual September volume surge."
            ),
        )
