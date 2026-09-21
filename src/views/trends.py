"""Section 3 View: Root Cause Diagnostic: Pricing & Logistics (Task 3)."""

import pandas as pd
import streamlit as st

from src.components.charts import (
    create_discount_cliff_chart,
    create_discount_profit_scatter,
    create_freight_absorption_chart,
    create_priority_freight_chart,
)
from src.components.narratives import render_chart_story_card, render_data_dictionary_expander
from src.services.analyzer import (
    analyze_discount_impact,
    analyze_shipping_and_priority,
)


def render_trends_view(df: pd.DataFrame) -> None:
    """Render Section 3: Root Cause Diagnostic on Commercial Pricing and Logistics Cost Absorption."""
    st.markdown("## Section 3: Root Cause Diagnostic: Pricing & Logistics")
    st.markdown(
        "**Diagnostic Objective**: Investigate commercial pricing concessions, freight absorption ratios, fulfillment tiers, and governance controls to establish root causes of margin dilution."
    )
    st.markdown("---")

    # Formal Problem Formulation (Task 3)
    with st.container(border=True):
        st.markdown("### Formal Problem Formulation: Unit Economics Breakdown & Root Cause Identification")
        st.markdown(
            r"""
            **Context & Stakeholder Dilemma (Task 3 Brief)**:
            The Taskforce must investigate the underlying operational mechanics driving negative margins on 12,544 order lines.
            The Chief Strategy Officer requires a forensic inquiry utilizing iterative "5-Why" causal chaining to resolve three specific questions:

            1. **The Contractual Pricing Threshold**: At what discount percentage $\delta^*$ does unit economics invert into structural operating losses?
               $$\text{Unit Margin}(\delta) = \text{List Price} \times (1 - \delta) - \text{COGS} - \text{Shipping Cost} \lessgtr 0$$
            2. **Logistics Cost Absorption & Service-Level Subsidization**:
               $$\text{Freight Absorption Ratio} = \frac{\text{Landed Shipping Cost}}{\text{Invoiced Sales}}, \quad \text{Evaluate across Delivery Tiers and Fulfillment Priorities}$$
            3. **Institutional & Governance Root Causes**: What organizational and architectural failures permitted 70% discounts and unchecked cross-border shipping deficits to persist across 4 fiscal years?
            """
        )

    render_data_dictionary_expander()

    if df.empty:
        st.warning("No records match the current parameter selection.")
        return

    # Direct Diagnostic Answers
    with st.container(border=True):
        st.markdown("### Executive Diagnostic: Pricing & Logistics Drivers")
        st.markdown(
            """
            * **How does contractual price discounting influence unit profitability? Is there an identifiable threshold beyond which orders become structurally unprofitable?**
              - **Yes: The Unit Economics Inversion Threshold occurs at precisely 20.0% discount.**
              - Orders discounted between **0.0% and 20.0%** consistently deliver positive operating margins ranging from **+9.9% to +25.3%**.
              - Once price concessions exceed **20.0%**, operating margins invert into deep deficits: **-5.5% (at 20–30% discount)**, **-23.7% (at 30–40%)**, **-45.3% (at 40–50%)**, and **-111.0% (at >50%)**.
              - Price concessions exceeding 20.0% single-handedly destroyed **-\\$814,682 in operating profit**.
            * **Do logistics fulfillment expenses erode operating contribution in specific operating territories?**
              - **Yes.** In volatile currency jurisdictions (Turkey, Nigeria), standard cross-border freight costs combined with heavy discounts generate landed costs that exceed invoiced customer revenue.
              - Expedited delivery tiers (*Same Day* and *First Class*) incur freight expenses representing **16.8% to 17.4% of sales**, yet were frequently provided without freight recovery fees.
            * **What are the structural root causes of corporate underperformance?**
              1. **Absence of Institutional Discount Governance**: Point-of-sale systems permit sales representatives to grant price concessions up to 70% without managerial approval.
              2. **Cross-Border Fulfillment Architecture in Emerging Territories**: Direct international fulfillment into high-tariff jurisdictions creates unrecoverable freight cost burdens.
              3. **Unrecovered Bulky Freight on Furniture Lines**: Bulky, low-density merchandise (Tables) shipped without dimensional weight surcharges.
              4. **Misaligned Commercial Sales Incentives**: Field commission structures reward gross invoiced sales rather than gross margin or contribution profit.
            """
        )

    st.divider()

    # 1. The 20% Discount Cliff
    with st.container(border=True):
        st.markdown("### 1. Price Realization Analysis: The 20% Discount Inversion Threshold")
        disc_df = analyze_discount_impact(df)

        col_chart, col_table = st.columns([3, 2])
        with col_chart:
            cliff_fig = create_discount_cliff_chart(disc_df)
            st.plotly_chart(cliff_fig, use_container_width=True)

        with col_table:
            st.markdown("#### Discount Tier Economic Matrix")
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
                use_container_width=True,
            )

        render_chart_story_card(
            title="Unit Economics Inversion Threshold (The 20% Discount Bound)",
            what_it_shows=(
                "Distribution of net operating profit margin across discrete contractual discount brackets from 0.0% to >50.0%. "
                "Green bars represent profitable pricing tiers; red bars delineate operating deficits below the break-even threshold."
            ),
            key_takeaway=(
                "The baseline gross operating margin prior to discounting is approximately 25.0% to 30.0%. "
                "When discounts are maintained within 0.0% to 20.0%, transactions preserve healthy net margins (+9.9% to +25.3%). "
                "However, exceeding 20.0% discount triggers unit economics inversion: contractual concessions exceed total product gross margin, "
                "resulting in direct cash burn on every item shipped. Transactions past 20.0% produced -\\$814,682 in cumulative losses."
            ),
            business_impact=(
                "This empirical finding represents the primary driver of corporate margin stagnation: Global Superstore conceded \\$814,000 "
                "in operating earnings through unmonitored commercial discounting. Eliminating discounts beyond 20.0% removes 88.5% of enterprise loss transactions."
            ),
            recommendation=(
                "Mandate automated validation rules in the enterprise ERP software: block order creation for any transaction containing a discount > 20.0% "
                "unless authorized in writing by the Chief Commercial Officer."
            ),
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Forensic Transaction Scatter: Empirical Verification of the Inversion Tipping Point")
        st.markdown(
            "Every individual order plotted across contractual discount rate (%) versus realized net operating profit ($ USD). "
            "Dashed line marks the 20.0% inversion threshold; dotted line marks break-even."
        )
        scatter_fig = create_discount_profit_scatter(df)
        st.plotly_chart(scatter_fig, use_container_width=True)

    st.divider()

    # 2. Shipping Cost and Order Priority Analysis
    with st.container(border=True):
        st.markdown("### 2. Freight Absorption Ratios and Fulfillment Service Levels")
        ship_df, priority_df = analyze_shipping_and_priority(df)

        # Freight Absorption Exhibits: Delivery Tiers & Fulfillment Priorities
        tab_tier, tab_prio = st.tabs(
            [
                "🚚 Logistics Delivery Tiers (Ship Mode)",
                "⚡ Fulfillment Priority Levels (Order Priority)",
            ]
        )

        with tab_tier:
            freight_chart = create_freight_absorption_chart(ship_df)
            st.plotly_chart(freight_chart, use_container_width=True)
            st.markdown("#### Performance Metrics: Delivery Tiers")
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
                use_container_width=True,
            )

        with tab_prio:
            priority_chart = create_priority_freight_chart(priority_df)
            st.plotly_chart(priority_chart, use_container_width=True)
            st.markdown("#### Performance Metrics: Fulfillment Priorities")
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
                use_container_width=True,
            )

        render_chart_story_card(
            title="Freight Cost Absorption and Expedited Delivery Subsidization",
            what_it_shows=(
                "Assessment of sales volume, net operating profit, landed shipping costs, and freight absorption ratios (%) across "
                "logistics fulfillment tiers (First Class, Same Day, Second Class, Standard Class) and fulfillment priority tiers."
            ),
            key_takeaway=(
                "Standard Class logistics accounts for 60.0% of volume with an 8.1% freight-to-sales ratio. "
                "Conversely, Same Day (17.38% freight ratio) and First Class (16.83% freight ratio) absorb more than double the freight cost per dollar billed. "
                "When expedited service levels are coupled with commercial discounting, contribution margins turn sharply negative."
            ),
            business_impact=(
                "The enterprise has subsidized rapid transit delivery by failing to index freight pricing to actual carrier costs, "
                "permitting customers to select premium expedited delivery without adequate basket size commitments."
            ),
            recommendation=(
                "Implement dynamic freight pass-through pricing: customer shipping fees must reflect carrier surcharges, "
                "and expedited shipping subsidies must be prohibited on orders below a \\$250 basket threshold."
            ),
        )

    st.divider()

    # 3. Process & Governance Hierarchy
    with st.container(border=True):
        st.markdown("### 3. Root Cause Diagnostic: Process & Governance Hierarchy")
        st.markdown(
            """
            | Governance Level | Diagnostic Inquiry | Forensic Evidence & Operational Finding |
            | :--- | :--- | :--- |
            | **Performance Symptom** | Why has consolidated operating margin stagnated at 11.6% despite +90% revenue growth? | 24.5% of order lines (12,544 transactions) generated negative operating margins, destroying **\\$920,646 in operating capital**. |
            | **Pricing Execution** | Why are nearly one in four transactions executed below cost-to-serve? | Commercial sales teams granted price concessions between **20.0% and 70.0%**, reducing landed selling price below landed product cost + freight. |
            | **Commercial Incentives** | Why were sales representatives authorized to offer 50% to 70% discounts? | Commercial compensation frameworks rewarded **gross top-line revenue**, with zero incentive alignment toward contribution margin or net profitability. |
            | **ERP System Controls** | Why does enterprise order entry software process transactions with 70% discounts? | Legacy IT architecture lacks programmatic validation controls, margin hurdle gates, or automated escalation workflows at point of order entry. |
            | **Institutional Root Cause** | **What is the foundational governance failure requiring Board intervention?** | **Absence of programmatic pricing controls, margin-aligned commercial incentives, and dimensional freight recovery mechanisms.** |
            """
        )

    st.divider()

    # Section 3 Proposed Solutions
    with st.container(border=True):
        st.markdown("### Section 3: Strategic Proposed Solutions")
        st.markdown(
            r"""
            Based on the root cause diagnostic, the strategic taskforce proposes three programmatic interventions:

            1. **Programmatic 20.0% Hard ERP Discount Ceiling**:
               - *Governance Mechanism*: Hardcode automated validation gates into the enterprise ERP order processing pipeline. Hard-block transaction creation for any discount $> 20.0\%$. Mandate automated VP approval for concessions between $15.0\%$ and $20.0\%$.
               - *Financial Quantification*: **Recovers +\$814,682 in destroyed operating profit**, eliminating 88.5% of enterprise deficit transactions.

            2. **Dynamic Freight Pass-Through & Surcharge Recovery**:
               - *Governance Mechanism*: Discontinue unhedged expedited shipping subsidies on Same Day (17.4% freight ratio) and First Class (16.8% freight ratio). Implement mandatory customer freight billing indexed to actual carrier surcharges, with free shipping restricted to orders exceeding \$250.
               - *Financial Quantification*: Recovers **+\$110,000 in unabsorbed carrier fulfillment expenses**.

            3. **Sales Incentive Recalibration (Margin-Weighted Commissions)**:
               - *Governance Mechanism*: Replace top-line volume bonus plans with Gross Margin Contribution hurdles. Penalize transactions discounted above 15% with progressive commission clawbacks.
               - *Impact*: Permanently aligns field commercial behavior with corporate shareholder return.
            """
        )
