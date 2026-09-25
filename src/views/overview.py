"""Chapter 1 View: The Verdict on the Rumours - Multi-Year Performance (Task 1)."""

import pandas as pd
import streamlit as st

from src.components.charts import (
    create_monthly_trend_chart,
    create_quarterly_seasonality_chart,
    create_yoy_growth_chart,
)
from src.components.narratives import render_chart_story_card, render_data_dictionary_expander
from src.components.story import render_story_ribbon
from src.services.analyzer import (
    compute_monthly_trend,
    compute_quarterly_seasonality,
    compute_yoy_growth,
)


def render_overview_view(df: pd.DataFrame) -> None:
    """Render Chapter 1: the verdict on whether Global Superstore is underperforming."""
    render_story_ribbon(
        "ch1",
        "The rumours say the company is dying. The data says otherwise: sales grew +90% and profit +102% from "
        "2011 to 2014. The real problem is margin, stuck near 11.6% all four years.",
        "Ch. 2 - Where It Leaks: Four Countries, One Product, One Market",
    )
    st.markdown("## Chapter 1 - The Verdict: Sales Doubled, Margin Didn't Move")
    st.markdown(
        "**What this chapter shows**: revenue rose from \\$2.26M to \\$4.30M and operating profit from \\$249K to "
        "\\$504K between 2011 and 2014, yet the margin band never left 11-12%. The year-by-year numbers below "
        "separate the growth story from the profitability story."
    )
    st.markdown("---")

    # Core Business Problem & Key Questions
    with st.container(border=True):
        st.markdown("### The Core Question: Are Sales Stalling or Growing?")
        st.markdown(
            """
            **What we're investigating**:
            There have been rumors that Global Superstore is losing money and running out of steam. 
            To test whether that's true, we looked at all 51,290 orders between 2011 and 2014 to answer three practical questions:

            1. **Are sales actually dropping, or is revenue growing?**
               Did the business stop growing, or are sales still heading upward?
            2. **Why didn't profit margins improve as the business got bigger?**
               Normally, when a company doubles in size, costs per order drop and profit margins go up. Why did our margin stay flat at ~11.6%?
            3. **Is the problem everywhere, or just in a few spots?**
               Are we losing money across the whole company, or is the damage coming from just a handful of countries and products?
            """
        )

    render_data_dictionary_expander()

    if df.empty:
        st.warning("No data available under the current parameter selection.")
        return

    # Direct Answers to the Key Questions
    with st.container(border=True):
        st.markdown("### Key Findings from the 4-Year Numbers")
        st.markdown(
            """
            * **Are sales and profits going up, flat, or declining?**
              - **Both sales and profits grew impressively.** Annual sales jumped from **\\$2,259,451 in 2011** to **\\$4,299,866 in 2014** — an overall growth of **+90.3%** (+26.3% in 2014 alone).
              - Operating profit more than doubled in the same period, growing from **\\$248,941 (2011)** to **\\$504,166 (2014)**, an increase of **+102.5%**.
            * **Is our profit margin getting better or worse?**
              - **The profit margin is completely flat.** It hovered in a narrow range of **11.0% (2011)**, **11.5% (2012)**, **12.0% (2013)**, and **11.7% (2014)**. Even though order volume doubled, the company didn't become more profitable per dollar of sales because price discounts ate up the gains.
            * **Is the whole business struggling, or just a few areas?**
              - **The problem is isolated to specific areas.** Most of the business is healthy: 75.5% of orders made money, delivering **\\$2.39M in profit**. The losses come from just four countries (Turkey, Nigeria, Netherlands, Honduras) and one product line (Tables).
            """
        )

    st.divider()

    # YoY Annual Growth Analysis
    yoy_df = compute_yoy_growth(df)

    with st.container(border=True):
        st.markdown("### Year-over-Year Growth (2011–2014)")
        yoy_chart = create_yoy_growth_chart(yoy_df)
        st.plotly_chart(yoy_chart, width="stretch")

        render_chart_story_card(
            title="Sales Doubled, but Profit Margins Stayed Flat",
            what_it_shows=(
                "Annual sales (blue bars), operating profit (green bars), and profit margin percentage "
                "(yellow line) across all 51,290 orders from 2011 through 2014."
            ),
            key_takeaway=(
                "Sales grew steadily every single year (+18.5% in 2012, +27.2% in 2013, +26.3% in 2014). "
                "Profits grew from $249K to $504K. But profit margin stayed stubbornly flat at around 11.6% to 11.9%. "
                "As the business got bigger, it failed to reap the benefits of scale because discounts ate up the extra profit."
            ),
            business_impact=(
                "Rumors that revenue has stalled are completely false. The real challenge is that as orders doubled from "
                "4,440 to 8,531 per year, sales teams gave away more and more discounts, canceling out the profit gains."
            ),
            recommendation=(
                "Reward sales teams based on the profit they bring in, rather than just total revenue booked. "
                "This stops reps from giving huge discounts just to hit sales targets."
            ),
        )

        st.markdown("#### Annual Performance Numbers")
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
            width="stretch",
        )

    st.divider()

    # Monthly / Quarterly Seasonality
    with st.container(border=True):
        st.markdown("### Monthly Sales and Profit Trends")
        st.markdown(
            "Looking at orders month by month shows that sales surge in the fourth quarter (October to December), driven by holiday shopping and year-end corporate buying."
        )
        monthly_df = compute_monthly_trend(df)
        trend_chart = create_monthly_trend_chart(monthly_df)
        st.plotly_chart(trend_chart, width="stretch")

        render_chart_story_card(
            title="Monthly Sales Patterns and Year-End Surges",
            what_it_shows=(
                "A month-by-month look at total sales (blue area) and profit (green line) over the full 48-month period, "
                "showing regular seasonal cycles."
            ),
            key_takeaway=(
                "Every single year follows the exact same pattern: Q1 starts slow, Q2 and Q3 pick up speed, and Q4 experiences "
                "a massive rush, generating about 35% of the entire year's sales."
            ),
            business_impact=(
                "During the year-end rush, sales reps rush to hit their annual targets and hand out heavy discounts. "
                "At the same time, shipping carriers charge peak holiday rates, squeezing profit margins right when sales volume is highest."
            ),
            recommendation=(
                "Set clear discount limits before Q4 starts and lock in shipping rates with carriers by August to protect year-end profits."
            ),
        )

        st.markdown("#### Quarterly Breakdown (Q1–Q4 Comparison)")
        st.markdown(
            "This table and chart show how much of each year's sales happened in each quarter."
        )
        quarterly_df = compute_quarterly_seasonality(df)
        q_chart = create_quarterly_seasonality_chart(quarterly_df)
        st.plotly_chart(q_chart, width="stretch")

        render_chart_story_card(
            title="Q4 Consistently Accounts for Over One-Third of Annual Sales",
            what_it_shows="Sales dollars and percentage share of total revenue for each quarter (Q1 to Q4) from 2011 to 2014.",
            key_takeaway=(
                "Q4 consistently generates between 31.5% and 36.8% of the company's annual revenue — more than double what is sold in Q1 (~15%)."
            ),
            business_impact=(
                "The year-end rush puts serious pressure on operations: aggressive discounting combined with peak holiday shipping fees "
                "erodes the profits that the business worked all year to build."
            ),
            recommendation="Lock in shipping capacity in advance and restrict discretionary sales discounts during November and December.",
        )

        st.markdown("##### Quarterly Performance Table")
        st.dataframe(
            quarterly_df.style.format(
                {
                    "Sales": "${:,.2f}",
                    "Profit": "${:,.2f}",
                    "Profit_Margin": "{:.2f}%",
                    "Quarter_Share_Pct": "{:.1f}%",
                    "Orders": "{:,}",
                }
            ),
            width="stretch",
        )

    st.divider()

    # Chapter 1 - what this evidence changes
    with st.container(border=True):
        st.markdown("### Chapter 1 Actions: Protect the Growth")
        st.markdown(
            r"""
            Based on the 4-year trend analysis, we recommend three practical steps:

            1. **Pay Sales Teams for Profit, Not Just Revenue**:
               - *Action*: Stop basing sales bonuses solely on total sales volume. Tie commissions to actual profit (Sales minus Product Cost minus Shipping).
               - *Expected Result*: Stops reps from closing money-losing deals just to hit their sales quotas.

            2. **Lock In Shipping Rates and Discount Limits Ahead of Q4**:
               - *Action*: Since Q4 brings in ~35% of all annual sales, negotiate shipping rates with freight carriers by August, and restrict special discounts from mid-October through December.
               - *Expected Result*: Protects profits against last-minute panic discounting and expensive holiday shipping surcharges.

            3. **Set a Minimum Profit Standard (10% Floor)**:
               - *Action*: Require special manager approval for any large order that yields less than a 10% profit margin.
               - *Expected Result*: Ensures that healthy sales growth (+23.9% a year) actually translates into higher profit margins.
            """
        )
