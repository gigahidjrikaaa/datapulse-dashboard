"""Executive Summary view — One-pager briefing for the Board of Directors with institutional advisory rigor."""

import pandas as pd
import streamlit as st

from src.components.charts import create_ebitda_bridge_chart
from src.components.metrics import render_kpi_cards
from src.components.narratives import render_data_dictionary_expander
from src.services.analyzer import compute_overview_kpis, simulate_turnaround_impact


def render_executive_summary_view(df: pd.DataFrame) -> None:
    """Render the one-page executive memorandum for the Board of Directors."""
    st.markdown("# Executive Memorandum: Strategic Performance Diagnostic")
    st.markdown(
        "**Board of Directors Advisory** | Prepared by the Special Strategy & Operations Taskforce"
    )
    st.markdown("---")

    # Global Data Dictionary & Financial Methodology
    render_data_dictionary_expander()

    # Formal Problem Formulation
    with st.container(border=True):
        st.markdown("### Formal Problem Formulation: Executive Turnaround Diagnostic & Corporate Governance Inquiry")
        st.markdown(
            r"""
            **Macro Strategic Inquiry for the Board of Directors**:
            External market skepticism suggests that Global Superstore is facing structural commercial distress. The Board of Directors has commissioned a forensic diagnosis across the complete 51,290-transaction ledger (FY2011–FY2014) to resolve four fundamental governance questions:

            1. **The Growth vs. Governance Paradox**: Has top-line demand stalled, or has unmonitored commercial expansion eroded profitability?
               $$\text{Evaluate: } \text{CAGR}(\text{Sales}) \text{ vs. } \Delta \text{Operating Margin}$$
            2. **Forensic Value Leakage Quantification**: Where does capital bleed across markets, product lines, and pricing structures?
               $$\text{Quantify: } \sum_{i \in \text{Deficit}} |\text{Loss}_i| \quad \text{across Geography, Discount Bands, and SKUs}$$
            3. **Root Mechanism of Value Destruction**: What specific commercial policy enabled \$920K+ in transaction losses?
               $$\text{Identify: Threshold } d^* \text{ such that } \mathbb{E}[\text{Margin} \mid \text{Discount} > d^*] < 0$$
            4. **EBITDA Turnaround & Capital Recovery Roadmap**: How can leadership recover operating earnings without impairing healthy customer relationships?
               $$\text{Formulate: } \max \Delta \text{EBITDA} \quad \text{subject to customer retention constraints}$$
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
        st.markdown("### Executive Takeaway for the Board of Directors")
        st.markdown(
            """
            **Global Superstore is experiencing a commercial governance and margin dilution crisis, rather than a top-line growth failure.**
            
            * Gross invoiced sales expanded from **\\$2.26M (FY2011) to \\$4.30M (FY2014)**, reflecting a compound annual growth rate of **+23.9%** (+26.3% YoY in FY2014).
            * However, **24.5% of total order transactions (12,544 lines)** were executed below cost-to-serve, generating **\\$920,646 in cumulative negative margin drag** and depressing consolidated operating margin to **11.6%**.
            * The root causes are concentrated: **uncontrolled price concessions exceeding 20%** and unhedged freight subsidies in select overseas territories (Turkey, Nigeria, Netherlands).
            * Enforcing automated pricing controls, sovereign 3PL restructuring, and dimensional freight recovery provides a verified operational bridge to capture **+\$1,233,804 in net EBITDA (+84.1% expansion to \$2.70M at 19.9% margin)** under base case parameters (with gross unburdened loss elimination potential of up to **+\$920,646 / +62.7%** across all 12,544 deficit lines).
            """
        )

    st.divider()

    # 2. Executive Diagnostic Summary: Four Pillars of Commercial Performance
    st.markdown("### Executive Diagnostic Summary: Four Pillars of Commercial Performance")
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        with st.container(border=True):
            st.markdown(
                """
                #### Pillar I: Top-Line Expansion
                * **Market Rumor**: Revenue stagnation and loss of competitive positioning.
                * **Forensic Audit**: Sales grew **+90.3%** across the 4-year audit period, with annual order volume expanding from 4,440 to 8,531 orders.
                * **Diagnosis**: Top-line demand is strong, but corporate management rewarded gross sales without margin accountability.
                """
            )

    with p2:
        with st.container(border=True):
            st.markdown(
                """
                #### Pillar II: Profit Dilution
                * **Core Finding**: Nearly 1 in 4 transactions (24.5%) was sold at an operating loss.
                * **Financial Quantification**: Profitable orders contributed **\\$2.39M** in gross operating profit, which was depleted by **-\\$920K in losses**.
                * **Consolidated Result**: Reported operating profit stood at **\\$1.47M**, masking severe margin leakage.
                """
            )

    with p3:
        with st.container(border=True):
            st.markdown(
                """
                #### Pillar III: Structural Drivers
                * **Driver 1 (The 20% Discount Bound)**: Transactions with discounts > 20% destroyed **-\\$814K**, as price concessions exceeded gross margin.
                * **Driver 2 (Territorial Deficits)**: Turkey (-\\$98K) and Nigeria (-\\$81K) generated heavy cash burn via cross-border freight into currency-devalued markets.
                """
            )

    with p4:
        with st.container(border=True):
            st.markdown(
                """
                #### Pillar IV: EBITDA Recovery
                * **Immediate Intervention**: Hardcode a 20% discount lock into order entry software; require executive authorization for discounts > 15%.
                * **Channel Restructuring**: Transition underperforming international territories to third-party logistics (3PL) distributor models.
                * **Value Creation**: Unlocks **+\\$1.23M in Net EBITDA uplift** (+84.1% expansion), lifting operating margin from 11.6% to 19.9%.
                """
            )

    st.divider()

    # 3. Three Key Findings & Three Strategic Recommendations side by side
    col_findings, col_recs = st.columns(2)

    with col_findings:
        with st.container(border=True):
            st.markdown("### Three Key Empirical Findings")
            st.markdown(
                """
                1. **The 20% Discount Inversion Threshold**:
                   - Transactions discounted between 0% and 20% generate strong operating margins (**+9.9% to +25.3%**).
                   - Once discount rates exceed 20%, unit contribution collapses into steep deficits (**-5.5% to -111.0%**), generating **-\\$814,682 in cumulative net losses**.
                   - Sales teams utilized up to 70% discounts to achieve top-line quota targets without margin hurdle requirements.
                
                2. **Territorial Deficit Concentration**:
                   - Four sovereign jurisdictions—**Turkey (-\\$98.4K)**, **Nigeria (-\\$80.8K)**, **Netherlands (-\\$41.1K)**, and **Honduras (-\\$29.5K)**—account for nearly **\\$250K in operating deficits** (55.8% of all sovereign losses) due to high baseline discounting and direct international shipping costs.
                   
                3. **Tables Merchandise Portfolio Mispricing**:
                   - Across all 17 portfolio sub-categories, **Tables** represents the sole net deficit line (**-\\$64,083 cumulative loss** on \\$757K revenue, -8.5% margin), caused by heavy packaging dimensions, cross-border freight intensity, and 29.1% average price concessions.
                """
            )

    with col_recs:
        with st.container(border=True):
            st.markdown("### Three Strategic Turnaround Initiatives")
            st.markdown(
                """
                1. **Institutionalize Pricing Governance and Order Entry Controls**:
                   - *Policy*: Establish a standard discount cap at 15%. Mandate Vice President approval for concessions between 16% and 20%. Programmatically restrict order processing for discounts > 20%.
                   - *Financial Recovery*: **+\\$1,032,488 EBITDA recovery** by capping concessions at 20.0% across 11,328 transactions.
                   
                2. **Restructure Deficit International Operating Channels**:
                   - *Policy*: Terminate direct corporate fulfillment into Turkey and Nigeria. Transition accounts to in-country master distributors and bonded 3PL logistics networks with local currency indexing.
                   - *Financial Recovery*: **+\\$179,198 in sovereign deficit elimination** (and up to +\\$250K across all 4 key deficit territories).
                   
                3. **Implement Bulky Freight Pass-Through and Table Portfolio Rationalization**:
                   - *Policy*: Restructure commercial furniture contracts to include mandatory dimensional weight surcharges and minimum order volume commitments.
                   - *Financial Recovery*: **+\\$46,245 bulky freight recovery and +\\$80,000+ margin turnaround**, moving Tables from deficit to positive contribution.
                """
            )

    st.divider()

    # 4. Financial Opportunity Waterfall Callout
    with st.container(border=True):
        st.markdown("### Commercial Value Recovery Model")
        st.markdown(
            "Executive financial summary of baseline earnings, recoverable negative margin drag, and adjusted earnings potential."
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "Reported Operating Profit",
                f"${kpis['total_profit']:,.0f}",
                f"{kpis['profit_margin']:.1f}% Operating Margin",
                help="Current actual earnings after absorbing operating losses.",
            )
        with c2:
            st.metric(
                "Recoverable Negative Margin Drag",
                f"+${kpis['profit_loss_drag']:,.0f}",
                f"Wiped out by {kpis['loss_order_pct']:.1f}% of order lines",
                help="Cumulative dollar loss from transactions executed below cost-to-serve.",
            )
        with c3:
            potential_profit = kpis["total_profit"] + kpis["profit_loss_drag"]
            potential_margin = (potential_profit / kpis["total_sales"] * 100.0) if kpis["total_sales"] > 0 else 0
            st.metric(
                "Adjusted Operating Profit Potential",
                f"${potential_profit:,.0f}",
                f"{potential_margin:.1f}% Margin (+62.7% Upside)",
                help="Unburdened operating earnings potential under strict pricing governance.",
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
        st.markdown("### Executive Memorandum: Strategic Proposed Solutions & Turnaround Directive")
        st.markdown(
            r"""
            To permanently reverse margin dilution and capture **+\$1,233,804 in net EBITDA recovery (+84.1% expansion to \$2.70M at 19.9% margin)**, the Strategic Taskforce submits three immediate executive directives for Board ratification:

            1. **Directive I: Institutionalize Automated Pricing Governance (The 20% Rule)**:
               - Hardcode ERP price floor gating: standard maximum discretionary discount capped at 15%; 16%–20% requires Regional VP authorization; >20% strictly blocked at checkout.
               - Re-align sales incentives from gross invoiced volume to Net Margin Contribution.
               - *Projected EBITDA Impact*: **+\$1,032,488** through automated 20.0% order entry ceiling across 11,328 transactions.

            2. **Directive II: Sovereign Channel Transformation (Turkey, Nigeria, Netherlands)**:
               - Immediately cease direct cross-border corporate shipping to persistent deficit jurisdictions.
               - Transition Turkey and Nigeria into local master distributor agreements or bonded 3PL logistics networks with local-currency indexation.
               - *Projected EBITDA Impact*: **+\$179,198** in bilateral deficit elimination (Turkey -\$98.4K and Nigeria -\$80.8K).

            3. **Directive III: Bulky Freight Cost Recovery & Table SKU Rationalization**:
               - Implement mandatory dimensional weight freight surcharges on high-cube furniture (Tables).
               - Impose minimum order quantity (MOQ) hurdles and eliminate single-item express fulfillment for bulky freight.
               - *Projected EBITDA Impact*: **+\$46,245**, lifting Tables from -\$64K deficit into positive margin contribution.
            """
        )
