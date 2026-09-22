"""Executive Summary view — One-pager briefing for the Board of Directors with institutional advisory rigor."""

import pandas as pd
import streamlit as st

from src.components.charts import create_ebitda_bridge_chart
from src.components.metrics import render_kpi_cards
from src.components.narratives import render_data_dictionary_expander
from src.services.analyzer import compute_overview_kpis, simulate_turnaround_impact


def render_syndicate_roster() -> None:
    """Render the Syndicate 6 project members using native Streamlit card containers."""
    members = [
        {"name": "Giga Hidjrika Aura Adkhy", "id": "388", "role": "Syndicate Member"},
        {"name": "Safia Aisyah Nur Savanah", "id": "364", "role": "Syndicate Member"},
        {"name": "Adiva Fitri Khalishah", "id": "377", "role": "Syndicate Member"},
        {"name": "Azka Ghossani Amin", "id": "357", "role": "Syndicate Member"},
        {"name": "Nurul Aulia Rahmawati", "id": "359", "role": "Syndicate Member"},
        {"name": "Cindy Monica Manurung", "id": "384", "role": "Syndicate Member"},
        {"name": "Louis Alessandro", "id": "356", "role": "Syndicate Member"},
    ]

    with st.container(border=True):
        st.markdown("#### Syndicate 6 Advisory Team")
        st.caption("Prepared by Class A Syndicate 6 | Strategic Diagnostic & Advisory Deliverable")

        # Row 1: Members 1 to 4
        cols_row1 = st.columns(4)
        for idx in range(4):
            m = members[idx]
            with cols_row1[idx]:
                with st.container(border=True):
                    st.caption(f"Student ID: **{m['id']}**")
                    st.markdown(f"**{m['name']}**")
                    st.caption(m["role"])

        # Row 2: Members 5 to 7 + Syndicate Summary Card
        cols_row2 = st.columns(4)
        for idx in range(3):
            m = members[4 + idx]
            with cols_row2[idx]:
                with st.container(border=True):
                    st.caption(f"Student ID: **{m['id']}**")
                    st.markdown(f"**{m['name']}**")
                    st.caption(m["role"])

        with cols_row2[3]:
            with st.container(border=True):
                st.caption("Academic Syndicate")
                st.markdown("**Class A • Syndicate 6**")
                st.caption("7 Advisory Analysts")


def render_executive_summary_view(df: pd.DataFrame) -> None:
    """Render the one-page executive memorandum for the Board of Directors."""
    st.markdown("# Global Superstore Case | Executive Summary")
    st.markdown(
        "**Prepared by Class A Syndicate 6**"
    )
    render_syndicate_roster()
    st.markdown("---")

    # Global Data Dictionary & Financial Methodology
    render_data_dictionary_expander()

    # Core Business Problem & Questions
    with st.container(border=True):
        st.markdown("### Core Business Problem & Questions for the Board")
        st.markdown(
            """
            **What leadership needs to know**:
            There has been persistent concern that Global Superstore is facing commercial distress. To get to the bottom of this, we analyzed all 51,290 customer orders from 2011 through 2014 to answer four fundamental business questions:

            1. **Are sales actually slowing down, or are we giving away our profits?**
               Did customer demand stall, or did rapid expansion without price controls eat away at profitability?
            2. **Where is money leaking out of the business?**
               Which specific countries, product categories, and discount levels are draining cash?
            3. **What is the exact tipping point where sales lose money?**
               At what discount percentage does a sale stop making a profit and start costing the company money?
            4. **How do we fix it and recover the profit?**
               What practical steps can management take to recapture over $1.2M in profit without hurting good customer relationships?
            """
        )

    if df.empty:
        st.warning("No data available under the current parameter selection.")
        return

    # Top-level KPIs
    kpis = compute_overview_kpis(df)
    with st.container(border=True):
        st.markdown("### Executive Performance Pulse (2011–2014 Cumulative)")
        render_kpi_cards(kpis)

    st.divider()

    # 1. Executive Board Takeaway Callout
    with st.container(border=True):
        st.markdown("### Key Takeaway for Leadership")
        st.markdown(
            """
            **Global Superstore does not have a sales problem — it has a pricing and discount problem.**
            
            * **Sales are growing rapidly**: Total revenue almost doubled from **\\$2.26M in 2011 to \\$4.30M in 2014**, growing at an average of **+23.9% per year** (+26.3% in 2014 alone).
            * **Profits are being drained by money-losing sales**: Nearly **1 in 4 orders (12,544 orders, or 24.5%) was sold at a loss**, wiping out **\\$920,646 in potential profit** and pulling the overall profit margin down to **11.6%**.
            * **The root causes are simple and concentrated**:
              1. **Discounts above 20%**: Sales teams offered steep discounts (up to 70%) to hit top-line quotas, losing money on every unit shipped.
              2. **Subsidized shipping to expensive overseas markets**: High discounts paired with expensive direct international shipping caused severe cash drain in countries like Turkey, Nigeria, and the Netherlands.
              3. **Bulky furniture**: Tables were heavily discounted while shipping costs ate up the remaining margin.
            * **The path to recovery**: By capping discounts at 20% at checkout, switching to local distribution partners in loss-making countries, and charging oversized shipping fees on bulky items, the company can capture **+\\$1,233,804 in net EBITDA (+84.1% expansion to \$2.70M at 19.9% margin)**.
            """
        )

    st.divider()

    # 2. Executive Diagnostic Summary: Four Pillars of Performance
    st.markdown("### Executive Summary: The Four Pillars of Performance")
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        with st.container(border=True):
            st.markdown(
                """
                #### 1. Sales Growth
                * **The Concern**: Rumors that revenue has stalled and customers are leaving.
                * **What the Data Shows**: Sales surged **+90.3%** over 4 years, and annual orders jumped from 4,440 to 8,531.
                * **Takeaway**: Customer demand is strong. The issue is how sales reps price those orders.
                """
            )

    with p2:
        with st.container(border=True):
            st.markdown(
                """
                #### 2. Hidden Profit Leaks
                * **The Concern**: Why is the profit margin stuck at ~11% despite doubling sales?
                * **What the Data Shows**: Profitable orders generated **\\$2.39M**, but **-\\$920K was wiped out** by orders sold at a loss.
                * **Takeaway**: Nearly 1 in 4 orders lost money, dragging total reported profit down to **\\$1.47M**.
                """
            )

    with p3:
        with st.container(border=True):
            st.markdown(
                """
                #### 3. Why It Happened
                * **The 20% Discount Cliff**: Orders with discounts over 20% destroyed **-\\$814K** because price cuts exceeded product profit margins.
                * **High-Loss Countries**: Turkey (-\\$98K) and Nigeria (-\\$81K) bled money due to heavy discounts plus expensive cross-border shipping.
                """
            )

    with p4:
        with st.container(border=True):
            st.markdown(
                """
                #### 4. How to Fix It
                * **Immediate Rule**: Cap discounts at 20% at checkout; require manager approval for anything above 15%.
                * **Partner Locally**: Move high-cost foreign markets to local distribution partners.
                * **Value Created**: Unlocks **+\\$1.23M in profit** (+84.1% boost), lifting profit margin from 11.6% to 19.9%.
                """
            )

    st.divider()

    # 3. Three Key Findings & Three Strategic Recommendations side by side
    col_findings, col_recs = st.columns(2)

    with col_findings:
        with st.container(border=True):
            st.markdown("### Three Key Findings")
            st.markdown(
                """
                1. **The 20% Discount Cliff (Where Profit Disappears)**:
                   - Orders discounted between 0% and 20% make healthy profits (**+9.9% to +25.3% margins**).
                   - Once discounts exceed 20%, margins collapse into steep losses (**-5.5% down to -111.0%**), creating **-\\$814,682 in total losses**.
                   - Sales reps gave discounts as high as 70% to hit revenue targets because their commissions did not depend on profit.
                
                2. **Four Countries Drive Over Half the Losses**:
                   - Four countries—**Turkey (-\\$98.4K)**, **Nigeria (-\\$80.8K)**, **Netherlands (-\\$41.1K)**, and **Honduras (-\\$29.5K)**—account for nearly **\\$250K in total losses** (55.8% of all country losses) due to huge discounts combined with expensive overseas shipping.
                   
                3. **Tables Is the Only Product Line in the Red**:
                   - Across all 17 product lines, **Tables** is the only one losing money (**-\\$64,083 loss** on \\$757K in sales, -8.5% margin).
                   - Large packaging dimensions, high shipping costs, and an average discount of 29.1% make every table sale an automatic loss.
                """
            )

    with col_recs:
        with st.container(border=True):
            st.markdown("### Three Actionable Fixes")
            st.markdown(
                """
                1. **Lock In Checkout Pricing Controls**:
                   - *Action*: Set standard discounts at 15% or lower. Require Vice President approval for 16% to 20%. Automatically block any discount over 20% in the checkout system.
                   - *Profit Recovered*: **+\\$1,032,488** by capping discounts at 20% across 11,328 orders.
                   
                2. **Switch to Local Distribution Partners in High-Loss Countries**:
                   - *Action*: Stop shipping individual packages directly into Turkey and Nigeria. Partner with local distributors and warehouses that handle domestic delivery with local currency pricing.
                   - *Profit Recovered*: **+\\$179,198 saved** in Turkey and Nigeria (and up to +\\$250K across all four high-loss markets).
                   
                3. **Charge Oversized Shipping Fees on Heavy Furniture**:
                   - *Action*: Update furniture pricing to include standard oversized handling fees, stop offering free express shipping on bulky items, and drop the most unprofitable table models.
                   - *Profit Recovered*: **+\\$46,245 in recovered freight and +\\$80,000+ total turnaround**, turning Tables back into a moneymaker.
                """
            )

    st.divider()

    # 4. Financial Opportunity Waterfall Callout
    with st.container(border=True):
        st.markdown("### Profit Recovery Breakdown")
        st.markdown(
            "Overview of current profits, money lost on unprofitable orders, and what the business could earn with disciplined pricing."
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "Current Operating Profit",
                f"${kpis['total_profit']:,.0f}",
                f"{kpis['profit_margin']:.1f}% Profit Margin",
                help="Actual profit earned after absorbing all money-losing sales.",
            )
        with c2:
            st.metric(
                "Money Lost on Unprofitable Sales",
                f"+${kpis['profit_loss_drag']:,.0f}",
                f"Lost across {kpis['loss_order_pct']:.1f}% of orders",
                help="Total dollars lost from selling items below actual cost.",
            )
        with c3:
            potential_profit = kpis["total_profit"] + kpis["profit_loss_drag"]
            potential_margin = (potential_profit / kpis["total_sales"] * 100.0) if kpis["total_sales"] > 0 else 0
            st.metric(
                "Potential Profit (If Losses Stopped)",
                f"${potential_profit:,.0f}",
                f"{potential_margin:.1f}% Margin (+62.7% Upside)",
                help="What operating profit would be if loss-making transactions were eliminated.",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        # Visual Anchor Exhibit: Mini EBITDA Turnaround Bridge
        sim_summary = simulate_turnaround_impact(
            df=df,
            max_discount_cap=0.20,
            restructure_deficit_territories=True,
            table_freight_surcharge=15.0,
            volume_attrition_rate=0.05,
        )
        bridge_fig = create_ebitda_bridge_chart(sim_summary["bridge_components"])
        st.plotly_chart(bridge_fig, use_container_width=True)

    st.divider()

    # Executive Proposed Solutions & Turnaround Directive
    with st.container(border=True):
        st.markdown("### Recommended Action Plan for the Board")
        st.markdown(
            r"""
            To permanently stop profit erosion and unlock **+\$1,233,804 in net profit (+84.1% increase to \$2.70M at a 19.9% margin)**, the strategy taskforce recommends three immediate actions for Board approval:

            1. **Action 1: Enforce the 20% Discount Cap in the Ordering System**:
               - Program the checkout system: standard sales rep discounts capped at 15%; 16%–20% requires Regional VP sign-off; discounts over 20% are completely blocked.
               - Shift sales commissions from total revenue booked to actual gross profit generated.
               - *Expected Impact*: **+\$1,032,488** in recovered profit across 11,328 orders.

            2. **Action 2: Switch to Local Distribution Partners in Turkey and Nigeria**:
               - Stop shipping direct cross-border packages into chronic loss-making countries.
               - Partner with local in-country distributors and third-party logistics (3PL) warehouses with local currency pricing.
               - *Expected Impact*: **+\$179,198** in direct loss elimination across Turkey (-\$98.4K) and Nigeria (-\$80.8K).

            3. **Action 3: Add Oversized Shipping Fees and Fix Table Pricing**:
               - Add mandatory oversized shipping surcharges on heavy, bulky furniture like Tables.
               - Require minimum order sizes for bulky deliveries and eliminate free express shipping on large items.
               - *Expected Impact*: **+\$46,245 in shipping fees recovered**, lifting Tables from a -\$64K loss into solid profitability.
            """
        )
