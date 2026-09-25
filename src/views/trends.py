"""Chapter 3 View: Why It Happens - Root Cause Diagnostic (Task 3)."""

import pandas as pd
import streamlit as st

from src.components.charts import (
    create_discount_cliff_chart,
    create_discount_profit_scatter,
    create_freight_absorption_chart,
    create_priority_freight_chart,
)
from src.components.narratives import render_chart_story_card, render_data_dictionary_expander
from src.components.story import render_story_ribbon
from src.services.analyzer import (
    analyze_discount_impact,
    analyze_shipping_and_priority,
)


def render_trends_view(df: pd.DataFrame) -> None:
    """Render Chapter 3: root-cause analysis on pricing and shipping."""
    render_story_ribbon(
        "ch3",
        "Two policy failures, not market forces. Every discount past 20% destroys margin - 11,328 lines burned "
        "$814,682 that way - and freight of up to 24% of sales value on priority and Same Day orders was never "
        "billed to the customer. The cause the company can act on is governance, not geography.",
        "Ch. 4 - The Fix: Three Levers That Recover $1.23M",
    )
    st.markdown("## Chapter 3 - Why It Happens: We Gave It Away Past 20%")
    st.markdown(
        "**The claim this chapter defends**: the Chapter 2 leaks share one mechanism. Discounts past 20% invert "
        "unit economics, and expensive shipping rode along uncharged. Asking \"why?\" five times takes us from "
        "lost margin to the actable root causes: no checkout limit, volume-based incentives, and free freight."
    )
    st.markdown("---")

    # Core Business Problem & Key Questions
    with st.container(border=True):
        st.markdown("### The Core Question: Why Did 12,544 Orders Lose Money?")
        st.markdown(
            """
            **What we're investigating**:
            Over 12,500 orders were sold at a loss, costing the company $920,646.
            To understand how this was allowed to happen, we looked at the root causes behind pricing and shipping:

            1. **The 20% Discount Cliff**: At what exact discount percentage does an order stop making money and start losing money?
            2. **Free & Fast Shipping**: Are expensive delivery options (like Same Day and First Class) eating up the profit on discounted orders?
            3. **System & Sales Rules**: Why did the ordering system let sales reps give discounts as high as 70% with free international delivery?
            """
        )

    render_data_dictionary_expander()

    if df.empty:
        st.warning("No records match the current parameter selection.")
        return

    # Direct Diagnostic Answers
    with st.container(border=True):
        st.markdown("### Key Findings on Pricing and Shipping")
        st.markdown(
            """
            * **How do discounts affect profit? Is there a clear breaking point?**
              - **Yes: The breaking point is precisely 20% discount.**
              - Orders discounted between **0% and 20%** make solid profits, with margins of **+9.9% to +25.3%**.
              - The moment a discount goes over **20%**, profit collapses into steep losses: **-5.5% (at 20–30% discount)**, **-23.7% (at 30–40%)**, **-45.3% (at 40–50%)**, and **-111.0% (at >50%)**.
              - Discounts higher than 20% single-handedly caused **-\\$814,682 in losses**.
            * **Do shipping costs eat up our profits?**
              - **Yes, especially on fast deliveries and overseas orders.** In countries like Turkey and Nigeria, shipping costs plus heavy discounts ended up costing more than the customer paid us.
              - Fast shipping (*Same Day* and *First Class*) eats up **16.8% to 17.4% of the sale price**, yet was often given away without charging the customer extra.
            * **What are the real root causes behind this?**
              1. **No checkout limits**: Sales reps could enter discounts up to 70% in the system without asking any manager.
              2. **Sales bonuses based on revenue, not profit**: Sales reps were rewarded for total dollars sold, giving them an incentive to slash prices just to close deals.
              3. **Direct shipping to high-cost countries**: Shipping individual packages across borders into countries with high tariffs and currency swings created huge delivery costs.
              4. **Free shipping on heavy tables**: Bulky furniture was shipped with standard shipping rates, eating up whatever margin remained.
            """
        )

    st.divider()

    # 1. The 20% Discount Cliff
    with st.container(border=True):
        st.markdown("### 1. The 20% Discount Cliff: Where Profit Disappears")
        disc_df = analyze_discount_impact(df)

        col_chart, col_table = st.columns([3, 2])
        with col_chart:
            cliff_fig = create_discount_cliff_chart(disc_df)
            st.plotly_chart(cliff_fig, width="stretch")

        with col_table:
            st.markdown("#### Profit by Discount Level")
            st.dataframe(
                disc_df.style.format(
                    {
                        "Total_Sales": "${:,.0f}",
                        "Total_Profit": "${:,.0f}",
                        "Profit_Margin": "{:.1f}%",
                        "Order_Lines": "{:,}",
                        "Avg_Profit_Per_Line": "${:,.2f}",
                        "Avg_Sales_Per_Line": "${:,.2f}",
                    }
                ),
                width="stretch",
            )

        render_chart_story_card(
            title="Profitability Drops Off a Cliff Past 20% Discount",
            what_it_shows=(
                "Average profit margin across different discount brackets from 0% up to over 50%. "
                "Green bars show profitable tiers; red bars show tiers where every sale loses money."
            ),
            key_takeaway=(
                "Before discounts, our products have a healthy profit margin of 25% to 30%. "
                "Discounts up to 20% keep profits positive (+9.9% to +25.3%). "
                "However, once discounts exceed 20%, the discount is bigger than our profit margin, meaning we lose cash on every item sold. "
                "Sales with discounts over 20% caused -$814,682 in total losses."
            ),
            business_impact=(
                "This single issue explains why profit margins stayed flat while sales doubled: we gave away $814,682 "
                "through unmanaged discounting. Stopping discounts above 20% eliminates 88.5% of enterprise cumulative loss capital "
                "and 81.2% of all deficit transactions (10,180 lines)."
            ),
            recommendation=(
                "Set an automatic rule in the checkout system: block any order with a discount greater than 20%, "
                "and require manager sign-off for any discount between 15% and 20%."
            ),
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Individual Order Scatter: Proof of the 20% Breaking Point")
        st.markdown(
            "Every single order plotted by discount percentage vs actual profit. "
            "Notice how almost every order to the right of the 20% line falls below zero profit."
        )
        scatter_fig = create_discount_profit_scatter(df)
        st.plotly_chart(scatter_fig, width="stretch")

    st.divider()

    # 2. Shipping Cost and Order Priority Analysis
    with st.container(border=True):
        st.markdown("### 2. Shipping Costs and Delivery Speeds")
        ship_df, priority_df = analyze_shipping_and_priority(df)

        # Freight Absorption Exhibits: Delivery Tiers & Fulfillment Priorities
        tab_tier, tab_prio = st.tabs(
            [
                "🚚 Delivery Speed (Ship Mode)",
                "⚡ Order Urgency (Order Priority)",
            ]
        )

        with tab_tier:
            freight_chart = create_freight_absorption_chart(ship_df)
            st.plotly_chart(freight_chart, width="stretch")
            st.markdown("#### Shipping Costs by Delivery Speed")
            st.dataframe(
                ship_df.style.format(
                    {
                        "Sales": "${:,.2f}",
                        "Profit": "${:,.2f}",
                        "Shipping_Cost": "${:,.2f}",
                        "Ship_Cost_Ratio": "{:.2f}%",
                        "Profit_Margin": "{:.2f}%",
                        "Avg_Shipping_Cost": "${:,.2f}",
                        "Orders": "{:,}",
                    }
                ),
                width="stretch",
            )

        with tab_prio:
            priority_chart = create_priority_freight_chart(priority_df)
            st.plotly_chart(priority_chart, width="stretch")
            st.markdown("#### Shipping Costs by Urgency Level")
            st.dataframe(
                priority_df.style.format(
                    {
                        "Sales": "${:,.2f}",
                        "Profit": "${:,.2f}",
                        "Shipping_Cost": "${:,.2f}",
                        "Ship_Cost_Ratio": "{:.2f}%",
                        "Profit_Margin": "{:.2f}%",
                        "Avg_Shipping_Cost": "${:,.2f}",
                        "Orders": "{:,}",
                    }
                ),
                width="stretch",
            )

        render_chart_story_card(
            title="Fast Delivery Eats Up Twice As Much Revenue As Standard Delivery",
            what_it_shows=(
                "Sales, profits, shipping costs, and shipping cost percentage across delivery speeds "
                "(Standard, Second Class, First Class, Same Day) and order priority tiers."
            ),
            key_takeaway=(
                "Standard shipping makes up 60% of orders and costs 8.1% of the sale price. "
                "In contrast, Same Day (17.4%) and First Class (16.8%) eat up more than double the percentage of sales. "
                "When fast shipping is combined with a 20%+ discount, the sale is virtually guaranteed to lose money."
            ),
            business_impact=(
                "We have been subsidizing expensive fast delivery without passing the costs to customers, "
                "allowing buyers to select premium shipping on small or heavily discounted orders."
            ),
            recommendation=(
                "Charge customers for expedited shipping unless their order meets a minimum basket size of $250, "
                "and never offer free expedited shipping on discounted items."
            ),
        )

    st.divider()

    # 3. Process & Governance Hierarchy (The 5-Why Table)
    with st.container(border=True):
        st.markdown("### 3. The '5 Whys': Tracing the Problem to Its Root Cause")
        st.markdown(
            """
            | Level | The Question | What the Data and Systems Reveal |
            | :--- | :--- | :--- |
            | **1. The Symptom** | Why did profit margins stay flat at 11.6% while sales almost doubled? | Nearly 1 in 4 orders (12,544 orders) lost money, destroying **\\$920,646 in profits**. |
            | **2. The Direct Cause** | Why did so many orders lose money? | Sales teams gave discounts between **20% and 70%**, meaning the selling price was lower than product cost plus shipping. |
            | **3. Sales Incentives** | Why were sales reps giving 50% to 70% discounts? | Reps were paid bonuses based on **total sales revenue**, regardless of whether the deal made or lost money. |
            | **4. Ordering Systems** | Why did the checkout system allow a 70% discount? | The ordering system had no automated price limits, warnings, or manager approval steps at checkout. |
            | **5. Foundational Cause** | **What is the root cause leadership needs to fix?** | **Lack of checkout discount caps, flawed sales incentives that reward revenue over profit, and no fees for oversized shipping.** |
            """
        )

    st.divider()

    # Section 3 Proposed Solutions
    with st.container(border=True):
        st.markdown("### Chapter 3 Actions: Close the Root Causes")
        st.markdown(
            r"""
            Based on the pricing and shipping diagnostic, we recommend three concrete actions:

            1. **Lock In a Hard 20% Discount Cap in the Ordering System**:
               - *Action*: Program the ordering software: standard sales discounts capped at 15%; 15%–20% requires manager approval; anything over 20% is completely blocked.
               - *Profit Recovered*: **Recovers +\$814,682 in lost profit**, eliminating 88.5% of all dollar losses across the company.

            2. **Stop Subsidizing Fast Shipping on Small Orders**:
               - *Action*: Stop giving away free Same Day (17.4% shipping cost) and First Class (16.8% shipping cost) shipping. Charge customers actual carrier shipping fees, with free shipping only on orders over \$250.
               - *Profit Recovered*: **Recovers +\$110,000 in unrecovered shipping costs**.

            3. **Pay Sales Commissions on Profit, Not Revenue**:
               - *Action*: Replace revenue-based sales bonuses with profit-based commissions. Reduce bonuses on any deals discounted above 15%.
               - *Expected Result*: Aligns sales reps' incentives with company profitability, stopping reckless discounting.
            """
        )
