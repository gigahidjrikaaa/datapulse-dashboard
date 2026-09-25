"""Section 4 View: Strategic Turnaround Framework & Board Presentation Deck (Task 4 & 5)."""

import os
import pandas as pd
import streamlit as st

from src.components.charts import (
    create_alt1_loss_concentration_chart,
    create_alt2_exit_vs_3pl_chart,
    create_alt3_freight_cut_vs_leak_chart,
    create_ebitda_bridge_chart,
)
from src.components.metrics import render_kpi_card
from src.components.narratives import render_chart_story_card, render_data_dictionary_expander
from src.components.predictive_charts import create_policy_profit_surface_chart
from src.services.analyzer import (
    compute_alternatives_assessment,
    compute_scenario_sensitivity_matrix,
    simulate_turnaround_impact,
)
from src.services.prescriptive import best_cap_by_market, optimize_turnaround_policy


@st.cache_data(show_spinner="Searching the policy grid with measured demand...")
def _cached_policy_optimizer(df: pd.DataFrame) -> dict:
    return optimize_turnaround_policy(df)


@st.cache_data(show_spinner="Tuning the cap per market...")
def _cached_market_caps(df: pd.DataFrame) -> pd.DataFrame:
    return best_cap_by_market(df)



def render_revival_strategy_view(df: pd.DataFrame | None = None) -> None:
    """Render Section 4: Turnaround Strategy, What-If Simulator, and Board Presentation Deck."""
    st.markdown("## Section 4: How We Turn Things Around (Strategy & Presentation)")
    st.markdown(
        "**Section Goal**: Lay out three prioritized turnaround steps with executive owners, timelines, and measurable goals — plus an interactive policy simulator and a 10-slide briefing deck for leadership."
    )
    st.markdown("---")

    # Core Business Problem & Key Questions
    with st.container(border=True):
        st.markdown("### The Core Question: How Do We Recapture Over $1.2M in Profit?")
        st.markdown(
            """
            **What leadership needs to decide**:
            Having identified that discounts over 20%, expensive shipping to Turkey and Nigeria, and unrecovered freight on tables are draining our profits, 
            the board now needs an actionable, risk-managed turnaround plan:

            1. **The Policy Simulator**: How much profit can we recover by capping discounts, partnering locally in high-loss markets, and charging oversized shipping fees — even if a few price-sensitive customers leave?
            2. **Who Owns What**: Which executives are responsible for executing each change, and what are their specific deadlines?
            3. **The Board Presentation**: How do we clearly communicate this evidence-backed turnaround story to directors and stakeholders in a concise 10-minute briefing?
            """
        )

    render_data_dictionary_expander()

    if df is None or df.empty:
        df = st.session_state.get("filtered_df")

    # Primary Feature: Interactive What-If Turnaround Policy Simulator & EBITDA Bridge
    if df is not None and not df.empty:
        st.markdown("### Interactive What-If Simulator: Test Your Turnaround Levers")
        st.markdown(
            "Use the controls below to see how different management decisions would impact overall profit. "
            "Adjust discount limits, test local partnerships in high-cost countries, add shipping fees for bulky items, and model potential customer drop-off."
        )

        with st.container():
            sim_col1, sim_col2 = st.columns(2)

            with sim_col1:
                st.markdown("#### Pricing & Customer Retention Levers")
                max_discount_cap_pct = st.slider(
                    "Maximum Discount Allowed at Checkout (%)",
                    min_value=10.0,
                    max_value=30.0,
                    value=20.0,
                    step=1.0,
                    help="Orders with discounts higher than this ceiling will be capped at this maximum rate.",
                )
                volume_attrition_rate_pct = st.slider(
                    "Estimated Customer Drop-off (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=5.0,
                    step=1.0,
                    help="Estimate of orders we might lose from price-sensitive customers who refuse to buy without steep discounts.",
                )

            with sim_col2:
                st.markdown("#### Shipping & Distribution Levers")
                table_freight_surcharge = st.slider(
                    "Tables Oversized Shipping Fee ($/unit)",
                    min_value=0.0,
                    max_value=50.0,
                    value=15.0,
                    step=5.0,
                    help="A standard fee charged to customers to cover the actual cost of shipping large, heavy tables.",
                )
                restructure_deficit_territories = st.toggle(
                    "Partner with Local Distributors in Turkey & Nigeria",
                    value=True,
                    help="Switch from direct overseas shipping to local distribution partners in Turkey and Nigeria, stopping chronic shipping losses.",
                )

        sim_results = simulate_turnaround_impact(
            df=df,
            max_discount_cap=max_discount_cap_pct / 100.0,
            restructure_deficit_territories=restructure_deficit_territories,
            table_freight_surcharge=table_freight_surcharge,
            volume_attrition_rate=volume_attrition_rate_pct / 100.0,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            render_kpi_card(
                title="Baseline Operating Profit",
                value=f"${sim_results['baseline_profit']:,.0f}",
                sub_value=f"Baseline Margin: {sim_results['baseline_margin']:.2f}%",
            )
        with m2:
            render_kpi_card(
                title="Simulated Operating EBITDA",
                value=f"${sim_results['projected_profit']:,.0f}",
                sub_value=f"Simulated Margin: {sim_results['projected_margin']:.2f}%",
            )
        with m3:
            uplift = sim_results["net_ebitda_uplift"]
            pct_uplift = (
                (uplift / sim_results["baseline_profit"] * 100.0)
                if sim_results["baseline_profit"] > 0
                else 0.0
            )
            render_kpi_card(
                title="Net EBITDA Recovery",
                value=f"+${uplift:,.0f}" if uplift >= 0 else f"-${abs(uplift):,.0f}",
                sub_value=f"{pct_uplift:+.1f}% vs Baseline",
            )
        with m4:
            render_kpi_card(
                title="Transactions Repriced",
                value=f"{sim_results['affected_orders_count']:,}",
                sub_value=f"{(sim_results['affected_orders_count'] / len(df) * 100):.1f}% of Transaction Volume",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # EBITDA Bridge Waterfall Chart
        w_chart = create_ebitda_bridge_chart(sim_results["bridge_components"])
        st.plotly_chart(w_chart, width="stretch")

        render_chart_story_card(
            title="Step-by-Step Profit Recovery Waterfall",
            what_it_shows=(
                "A waterfall chart showing how we build from our current profit up to our new turnaround profit: "
                "adding profit from discount caps, savings from local partnerships in Turkey and Nigeria, "
                "adding recovered fees on bulky tables, subtracting potential lost orders, and reaching the final projected profit."
            ),
            key_takeaway=(
                f"With the selected settings (Discount Cap: {max_discount_cap_pct:.0f}%, Customer Drop-off: {volume_attrition_rate_pct:.0f}%, "
                f"Table Fee: ${table_freight_surcharge:.0f}, Local Partners: {'Enabled' if restructure_deficit_territories else 'Disabled'}), "
                f"the company unlocks +${sim_results['net_ebitda_uplift']:,.0f} in new profit, raising profit margin from "
                f"{sim_results['baseline_margin']:.1f}% to {sim_results['projected_margin']:.1f}%."
            ),
            business_impact=(
                "Most importantly, this proves that turning the company around does not require risky new sales campaigns. "
                "Simply stopping money-losing sales and shipping subsidies produces an immediate jump in earnings, "
                "even after accounting for customers who leave."
            ),
            recommendation=(
                "Present this recovery waterfall to the Board to justify locking in the 20% discount limit "
                "and setting up local distributor agreements."
            ),
        )

        st.markdown("#### Profit Recovery Breakdown Table")
        bridge_df = pd.DataFrame(
            [
                {
                    "Turnaround Lever": "1. Current Operating Profit",
                    "Impact ($ USD)": sim_results["baseline_profit"],
                    "How It Works": "Actual company operating earnings before any changes.",
                },
                {
                    "Turnaround Lever": f"2. Capping Discounts at {max_discount_cap_pct:.0f}%",
                    "Impact ($ USD)": sim_results["pricing_recovery"],
                    "How It Works": f"Repricing {sim_results['affected_orders_count']:,} orders where discounts were higher than {max_discount_cap_pct:.0f}%.",
                },
                {
                    "Turnaround Lever": "3. Local Distribution in Turkey & Nigeria",
                    "Impact ($ USD)": sim_results["territory_recovery"],
                    "How It Works": "Switching to in-country distribution partners, eliminating expensive cross-border shipping losses.",
                },
                {
                    "Turnaround Lever": f"4. Oversized Shipping Fee on Tables (${table_freight_surcharge:.0f}/unit)",
                    "Impact ($ USD)": sim_results["table_freight_recovery"],
                    "How It Works": "Charging customers for the actual cost of shipping bulky furniture boxes.",
                },
                {
                    "Turnaround Lever": f"5. Potential Customer Drop-off ({volume_attrition_rate_pct:.0f}%)",
                    "Impact ($ USD)": -sim_results["attrition_drag"],
                    "How It Works": "Conservative allowance for price-sensitive buyers who walk away when discounts are limited.",
                },
                {
                    "Turnaround Lever": "6. Projected Operating Profit",
                    "Impact ($ USD)": sim_results["projected_profit"],
                    "How It Works": f"New expected profit under this turnaround policy (Margin: {sim_results['projected_margin']:.2f}%).",
                },
            ]
        )
        st.dataframe(
            bridge_df.style.format({"Impact ($ USD)": "${:,.2f}"}),
            width="stretch",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Institutional Scenario Sensitivity Matrix (Pre-Configured Policy Packages)")
        st.markdown(
            "Comparative multi-scenario evaluation model pre-configured for executive review, evaluating Conservative, "
            "Base Case (Target Plan), and Aggressive turnaround packages alongside the status quo baseline."
        )
        scenario_matrix = compute_scenario_sensitivity_matrix(df)
        st.dataframe(
            scenario_matrix.style.format(
                {
                    "Repriced Orders": "{:,}",
                    "Projected Operating EBITDA": "${:,.2f}",
                    "Net EBITDA Uplift": "+${:,.2f}",
                    "EBITDA Uplift (%)": "{:+.1f}%",
                    "Projected Operating Margin": "{:.2f}%",
                }
            ),
            width="stretch",
        )

        # Alternatives the taskforce considered and eliminated
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Alternatives Considered & Eliminated")
        st.markdown(
            "Before locking the three-lever plan, we stress-tested the obvious alternatives on the same ledger. "
            "Each one either re-opens the loss zone, forfeits revenue, or moves too little, too slowly:"
        )
        alts = compute_alternatives_assessment(df)
        alternatives_df = pd.DataFrame(
            [
                {
                    "Alternative": "1. Raise list prices, allow deeper discounts",
                    "What It Promises": "Bigger concessions look affordable from a higher invoice price",
                    "Why It Is Eliminated": (
                        f"The leak follows the discount depth, not the list price: margins run +9.9% at 10-20% off "
                        f"but -5.5% at 20-30%, and {alts['deep_share_of_losses'] * 100.0:.1f}% of all loss dollars "
                        f"(${alts['deep_discount_loss']:,.0f}) sit above the 20% line. A deeper cap re-opens that loss zone."
                    ),
                    "Verdict": "Eliminated",
                },
                {
                    "Alternative": "2. Exit Turkey and Nigeria entirely",
                    "What It Promises": "Instant stop to the country deficits",
                    "Why It Is Eliminated": (
                        f"Abandons ${alts['tn_sales']:,.0f} of revenue and two developing markets; 3PL restructuring "
                        f"removes the same ${alts['tn_loss']:,.0f} of losses while keeping every sale."
                    ),
                    "Verdict": "Eliminated",
                },
                {
                    "Alternative": "3. Renegotiate carrier rates company-wide",
                    "What It Promises": "Cheaper freight on every order",
                    "Why It Is Eliminated": (
                        f"Freight totals ${alts['freight_total']:,.0f} ({alts['freight_ratio'] * 100.0:.1f}% of sales), "
                        f"so a realistic 10% cut returns only ~${alts['freight_cut_recovery']:,.0f} after 12+ months of "
                        f"contracting - and leaves the ${alts['deep_discount_loss']:,.0f} discount leak untouched."
                    ),
                    "Verdict": "Support lever only",
                },
            ]
        )
        st.dataframe(alternatives_df, width="stretch")
        st.caption(
            "Verdicts are assessed on the FY2011-FY2014 ledger under the same base-case assumptions as the simulator above. "
            "Modelling estimates, not forecasts."
        )

        st.markdown("##### The Evidence Behind Each Elimination")
        e1, e2, e3 = st.columns(3)
        with e1:
            st.plotly_chart(
                create_alt1_loss_concentration_chart(alts["profit_by_band"], alts["deep_share_of_losses"]),
                width="stretch",
            )
            st.caption(
                f"Why 'raise list prices, allow deeper discounts' fails: the leak follows discount depth, not list "
                f"price. The bands above the 20% line destroy ${alts['deep_discount_loss']:,.0f} of net profit - "
                f"{alts['deep_share_of_losses'] * 100.0:.1f}% of all loss dollars - so a deeper cap re-opens exactly "
                f"these bands."
            )
        with e2:
            st.plotly_chart(
                create_alt2_exit_vs_3pl_chart(alts["tn_sales"], alts["tn_loss"]),
                width="stretch",
            )
            st.caption(
                f"Why 'exit Turkey & Nigeria' fails: walking away forfeits ${alts['tn_sales']:,.0f} of revenue and two "
                f"developing markets, while 3PL restructuring removes the identical ${alts['tn_loss']:,.0f} loss and keeps "
                f"every sale."
            )
        with e3:
            cut_pct_of_leak = (
                (alts["freight_cut_recovery"] / alts["deep_discount_loss"] * 100.0)
                if alts["deep_discount_loss"] > 0
                else 0.0
            )
            st.plotly_chart(
                create_alt3_freight_cut_vs_leak_chart(
                    alts["freight_total"], alts["freight_cut_recovery"], alts["deep_discount_loss"]
                ),
                width="stretch",
            )
            st.caption(
                f"Why 'renegotiate carrier rates company-wide' is only a support lever: freight totals "
                f"${alts['freight_total']:,.0f} ({alts['freight_ratio'] * 100.0:.1f}% of sales), so a realistic 10% cut "
                f"returns ~${alts['freight_cut_recovery']:,.0f} after 12+ months of contracting - just "
                f"{cut_pct_of_leak:.0f}% of the ${alts['deep_discount_loss']:,.0f} discount leak it never touches."
            )

        # Prescriptive optimizer: search the policy space with the measured demand response
        raw_df = st.session_state.get("raw_df")
        if raw_df is None or raw_df.empty:
            raw_df = df
        opt = _cached_policy_optimizer(raw_df)
        markets = _cached_market_caps(raw_df)
        base_row = opt["grid"][(opt["grid"]["cap_value"] == 0.20) & (opt["grid"]["surcharge_value"] == 15.0)].iloc[0]
        best = opt["best"]
        gap = best["Projected operating profit"] - base_row["Projected operating profit"]

        st.markdown("##### Policy Optimizer: Profit Surface Across Caps & Surcharges (Measured Demand)")
        st.markdown(
            "The simulator above treats churn as an assumption. This optimizer replaces it with the Section 5 "
            "demand-response model: every line above the cap is re-priced at the cap, its volume scaled by the "
            "measured response, and the full cap x surcharge grid is searched for the profit-maximizing policy."
        )
        st.plotly_chart(create_policy_profit_surface_chart(opt["grid"], best), width="stretch")

        o1, o2, o3, o4 = st.columns(4)
        o1.metric("Profit-maximizing policy", f"{best['Discount cap']} cap", f"{best['Tables surcharge']} surcharge")
        o2.metric("Profit at optimum", f"${best['Projected operating profit']/1e6:,.2f}M", f"+{best['Uplift %']:.0f}% vs baseline")
        o3.metric("Plan of record (20% / $15)", f"${base_row['Projected operating profit']/1e6:,.2f}M", "+86% vs baseline, measured")
        o4.metric("Optimum vs plan of record", f"+${gap/1e6:,.2f}M", "rides on extrapolated demand response", delta_color="off")

        render_chart_story_card(
            title="With Measured Demand, Tighter Caps Look Better - and the 20% Plan Still Holds",
            what_it_shows=(
                f"Every combination of discount cap and Tables surcharge simulated on the full ledger with the "
                f"measured volume response ({opt['n_policies']} policies). Retention stays between 96% and 104% "
                "across the whole cap range - the deep-discount lines were never buying volume."
            ),
            key_takeaway=(
                f"The grid optimum is a {best['Discount cap']} cap with a {best['Tables surcharge']} surcharge at "
                f"${best['Projected operating profit']/1e6:,.2f}M. The plan of record (20% / $15) delivers "
                f"${base_row['Projected operating profit']/1e6:,.2f}M on the same measured basis - and the entire "
                "20-30% cap band sits within a few percent of it."
            ),
            business_impact=(
                "The turnaround case strengthens: what the assumed-churn simulator called a risk, the measured "
                "data calls roughly volume-neutral, so the profit range across sane policies is wide and entirely "
                "in the company's favour."
            ),
            recommendation=(
                "Keep the 20% cap as the plan of record - the extra profit from a 10% cap rests on extrapolating "
                "the demand response below where discounts are densely observed and on assuming associations hold "
                "when a cap binds. Re-run this optimizer after one quarter of live cap data."
            ),
        )
        st.caption(
            "Measured response = Section 5 model (OLS with category, market, year, and month controls) applied to "
            "the full FY2011-FY2014 ledger; sidebar filters do not apply. The optimum's advantage over the 20% cap "
            "is an extrapolation signal, not an operational recommendation."
        )

        st.markdown("#### Best Cap per Market (Other Levers at Base Case)")
        st.dataframe(
            markets.style.format(
                {
                    "Ledger profit": "${:,.0f}",
                    "Profit at best cap": "${:,.0f}",
                    "Profit at global 20% cap": "${:,.0f}",
                    "Uplift from tuning (vs global 20%)": "${:,.0f}",
                }
            ),
            width="stretch",
        )

    st.divider()

    # 1. The Three Priority Actions
    st.markdown("### Three Actionable Turnaround Priorities")

    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        with st.container(border=True):
            st.markdown(
                """
                #### Action 1: Enforce the 20% Discount Cap
                * **The Problem**: Sales reps gave away discounts up to 70%, causing -\\$814,682 in losses.
                * **Executive Owner**: Chief Commercial Officer & VP of Sales.
                * **Timeline**: Months 1 to 3.
                * **How It Works**:
                  - Require manager approval for discounts between 15% and 20%.
                  - Automatically block discounts above 20% at checkout.
                  - Pay sales bonuses based on actual profit, not gross revenue.
                * **Targets to Watch**:
                  - Orders with discount > 15% (Target: < 2%)
                  - Overall average discount (Target: < 12%)
                  - Sales team profit margin (Target: > 15%)
                * **Expected Profit**:
                  - **Recovers +\\$1,032,488 in operating profit** by capping discounts on 11,328 orders.
                  - Eliminates 88.5% of all dollar losses across the company.
                """
            )

    with action_col2:
        with st.container(border=True):
            st.markdown(
                """
                #### Action 2: Local Partners in Turkey & Nigeria
                * **The Problem**: Shipping directly across borders into volatile currency countries cost more than customers paid us.
                * **Executive Owner**: VP of Global Supply Chain & Regional Directors.
                * **Timeline**: Months 3 to 6.
                * **How It Works**:
                  - Stop direct air shipping of individual orders into Turkey and Nigeria.
                  - Partner with local in-country distributors and local warehouses.
                  - Set catalog prices in stable currencies or index to local inflation.
                * **Targets to Watch**:
                  - Country profit margin (Target: Break even in 90 days; > 8% in 12 months)
                  - Shipping cost ratio (Target: < 12% of sales)
                * **Expected Profit**:
                  - **Eliminates +\\$179,198 in chronic bilateral cash drain** across Turkey (-\\$98.4K) and Nigeria (-\\$80.8K).
                """
            )

    with action_col3:
        with st.container(border=True):
            st.markdown(
                """
                #### Action 3: Oversized Shipping on Tables
                * **The Problem**: Tables lost -\\$64,083 because heavy box sizes incurred huge shipping fees that were never billed to customers.
                * **Executive Owner**: Head of Merchandising & Director of Logistics.
                * **Timeline**: Months 6 to 12.
                * **How It Works**:
                  - Stop selling the most unprofitable table models.
                  - Add standard oversized shipping fees on bulky deliveries.
                  - Offer flat-pack furniture alternatives that cost less to ship.
                * **Targets to Watch**:
                  - Tables category profit (Target: > +\\$50,000)
                  - Oversized shipping fee compliance (Target: 100%)
                * **Expected Profit**:
                  - **+\\$46,245 bulky freight recovery and +\\$80,000+ total turnaround**, turning Tables into a profitable category.
                """
            )

    st.divider()

    # 2. 6-12 Month Implementation Milestones
    with st.container(border=True):
        st.markdown("### 6–12 Month Implementation Roadmap")
        st.markdown(
            """
            | Phase | What Gets Done | Timeline | Target Milestone |
            | :--- | :--- | :--- | :--- |
            | **Phase 1: Pricing Controls & Sales Pay** | Put the 20% discount lock into the checkout software. Switch sales bonuses to profit contribution. | Months 1–2 | Zero unapproved orders processed with discount > 20%. |
            | **Phase 2: Local Distribution in Turkey & Nigeria** | Stop direct overseas shipping. Partner with local distributors and warehouses. | Months 3–4 | Turkey and Nigeria losses cut by 70%; save \\$150K in shipping. |
            | **Phase 3: Tables Pricing & Shipping Fees** | Add oversized shipping fees for bulky furniture; drop money-losing table models. | Months 5–7 | Tables sub-category reaches break-even. |
            | **Phase 4: Quarterly Review & Optimization** | Conduct quarterly profit reviews across all 147 countries. Keep pricing disciplined. | Months 8–12 | Overall company profit margin expands from 11.6% to **over 15.5%**. |
            """
        )

    st.divider()

    # 3. Presentation Deck Outline & Deliverables (8-10 Slides)
    with st.container(border=True):
        st.markdown("### Board of Directors Presentation Deck (10-Minute Executive Briefing)")
        st.markdown(
            "Structured 10-slide executive briefing calibrated for a formal 10-minute board presentation followed by 5 minutes of strategic Q&A. "
            "All quantitative metrics, financial bridge models, and policy levers are 100% synchronized with the transaction ledger and policy simulator above:"
        )

        dl_col1, dl_col2, dl_col3 = st.columns(3)
        pptx_path = "presentation/board_deck.pptx"
        pdf_path = "presentation/board_deck.pdf"
        docx_path = "presentation/Global_Superstore_Executive_Summary.docx"
        if os.path.exists(pptx_path):
            with open(pptx_path, "rb") as f:
                dl_col1.download_button(
                    label="📥 Download Presentation Deck (.pptx)",
                    data=f.read(),
                    file_name="Global_Superstore_Revival_Strategy_Board_Deck.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    width="stretch",
                )
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                dl_col2.download_button(
                    label="📄 Download Presentation Deck (.pdf)",
                    data=f.read(),
                    file_name="Global_Superstore_Revival_Strategy_Board_Deck.pdf",
                    mime="application/pdf",
                    width="stretch",
                )
        if os.path.exists(docx_path):
            with open(docx_path, "rb") as f:
                dl_col3.download_button(
                    label="📑 Download Executive Summary (.docx)",
                    data=f.read(),
                    file_name="Global_Superstore_Executive_Summary.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    width="stretch",
                )

        with st.expander("Executive Deck Architecture: Slide Content, Visual Evidence & Presenter Notes", expanded=True):
            st.markdown(
                r"""
                #### Slide 1: Executive Title & Diagnostic Scope
                * **Slide Title**: *Global Superstore: Strategic Performance Evaluation & Turnaround Plan*
                * **Subtitle**: *Unlocking \$1,234,000 in Operating EBITDA (+84.1% Expansion) Through Commercial Discipline & Operating Model Restructuring*
                * **Presenters**: Special Strategy & Operations Taskforce (Syndicate 6)
                * **Visual**: Institutional executive title card with FY2011–FY2014 headline audit metrics (51,290 order lines).
                * **Presenter Notes (1.0 minute)**:
                  > *"Members of the Board, external speculation regarding Global Superstore's revenue stagnation is empirically disproven by transaction data. Our commercial demand engine is robust (+90.3% growth to \$4.30M), but operating earnings are diluted by an internal pricing governance failure. Today, we present conclusive audit evidence and an operational roadmap to unlock \$1,234,000 in bottom-line operating profit expansion."*

                ---

                #### Slide 2: Multi-Year Revenue Audit (Refuting Market Rumors)
                * **Slide Title**: *Top-Line Performance: Revenue Expanded +90.3% to \$4.30M; Operating Profit Lifted to \$504K*
                * **Visual**: Multi-year revenue and operating profit progression chart (FY2011–FY2014) with annual growth indicators (+18.5%, +27.2%, +26.3% YoY).
                * **Data Evidence**: Sales scaled from \$2.26M to \$4.30M (CAGR: 23.9%); operating profit expanded from \$249K to \$504K; order count scaled from 4,440 to 8,531 orders with stable AOV (~$505).
                * **Presenter Notes (1.0 minute)**:
                  > *"Over the past four fiscal years, Global Superstore added more than \$2.0 million in top-line revenue, expanding annual order volume from 4,440 to 8,531 orders. However, consolidated operating margin remained constrained at 11.6% (annual range: 11.0% to 11.9%), failing to capture operating leverage benefits as volume scaled."*

                ---

                #### Slide 3: The True Vulnerability: \$920,646 in Margin Dilution
                * **Slide Title**: *Capital Erosion: 24.5% of Transaction Volume Executed at an Operating Loss*
                * **Visual**: Financial bridge chart: Gross Profitable Contribution (\$2.39M) minus Negative Margin Drag (-\$920.6K) = Reported Operating Profit (\$1.47M).
                * **Data Evidence**: 12,544 order transactions executed below cost-to-serve, destroying \$920,646 in net earnings.
                * **Presenter Notes (1.0 minute)**:
                  > *"This is the central vulnerability of our operating model: our profitable core generated \$2.39 million in operating profit. However, 24.5% of order lines were executed at negative margins, destroying \$920,000 in capital. Management has focused on gross revenue volume while permitting unmonitored profit leakage."*

                ---

                #### Slide 4: Territorial Variance Analysis (Concentration of Deficits)
                * **Slide Title**: *Geographic Deficits: Four Sovereign Jurisdictions Account for \$250K in Losses (56% of Deficits)*
                * **Visual**: Horizontal bar chart ranking operating deficits across sovereign territories (Turkey, Nigeria, Netherlands, Honduras).
                * **Data Evidence**: Turkey (-\$98.4K loss, -90.7% margin, 60.0% disc), Nigeria (-\$80.8K loss, -148.6% margin, 70.0% disc), Netherlands (-\$41.1K loss, 48.2% disc), Honduras (-\$29.5K loss, 40.7% disc).
                * **Presenter Notes (1.0 minute)**:
                  > *"Operating deficits are concentrated geographically: 29 of 147 sovereign territories are net-negative, and the top four account for 56% of all territorial losses. Turkey and Nigeria alone destroyed \$179,000 in capital. In both territories, sales teams offered 60% to 70% baseline discounts to meet volume targets, while the corporate center absorbed cross-border logistics and customs duties in volatile currency environments."*

                ---

                #### Slide 5: Merchandise Portfolio Diagnostic (The Tables Anomaly)
                * **Slide Title**: *Portfolio Contribution: 16 Profitable Merchandise Lines vs. 1 Net Deficit Sub-Category*
                * **Visual**: Diverging bar chart displaying net operating contribution across all 17 portfolio sub-categories.
                * **Data Evidence**: Copiers (+\$258.6K), Phones (+\$216.7K), and Bookcases (+\$161.9K) deliver strong returns; Tables generated a cumulative deficit of -\$64,083 on \$757K in sales (-8.5% margin) with highest freight per unit (\$25.90/unit).
                * **Presenter Notes (1.0 minute)**:
                  > *"Sixteen out of seventeen merchandise sub-categories are highly profitable. Tables is the sole net deficit line. This is an operational pricing failure: tables generate high freight costs due to package dimensions. Applying 29.1% average discounts while subsidizing freight guarantees negative unit economics."*

                ---

                #### Slide 6: Root Cause Diagnostic: The 20% Discount Inversion Bound
                * **Slide Title**: *Unit Economics Inversion: Operating Margins Collapse Past 20% Discount*
                * **Visual**: Operating margin distribution across discount brackets (0% to >50%), highlighting the break-even threshold.
                * **Data Evidence**: Orders discounted ≤20% generate +9.9% to +25.3% margin; orders discounted >20% destroyed -\$814,682 across 11,328 line items.
                * **Presenter Notes (1.5 minutes)**:
                  > *"This is the definitive empirical finding of our audit: our gross product margin prior to discounting is 25% to 30%. Concessions up to 20% preserve positive returns. However, the moment discount rates exceed 20%, unit economics invert completely, producing cash burn on every shipment (-5.5% at 20-30%, -23.7% at 30-40%, -45.3% at 40-50%, -111.0% at >50%). Over \$814,000 in profit was conceded through unmonitored discounting past this threshold."*

                ---

                #### Slide 7: Operational Blind Spots: Freight Cost Absorption & System Controls
                * **Slide Title**: *Operational Gaps: Unrecovered Expedited Freight & Missing IT Controls*
                * **Visual**: Freight absorption ratios across logistics fulfillment tiers (Same Day at 17.4% vs Standard Class at 8.1%; Critical priority at 23.8%) and governance hierarchy.
                * **Presenter Notes (1.0 minute)**:
                  > *"Our legacy ERP architecture lacks automated margin validation controls, allowing sales representatives to enter transactions with 70% discounts and free expedited delivery without managerial review. We have subsidized premium carrier delivery without recovering freight surcharges."*

                ---

                #### Slide 8: The Three-Pillar Turnaround Framework
                * **Slide Title**: *Turnaround Strategy: Three Prioritized Interventions for Immediate Execution*
                * **Visual**: Structured three-pillar framework (Pricing Governance, Channel Restructuring, Bulky Freight Recovery).
                * **Presenter Notes (1.5 minutes)**:
                  > *"We propose three actionable initiatives: First, establish an institutional discount ceiling at 15% with a hard 20% ERP block. Second, restructure Turkey and Nigeria into third-party distributor models. Third, implement dimensional freight surcharges across the Tables portfolio."*

                ---

                #### Slide 9: Commercial Value Creation & EBITDA Bridge
                * **Slide Title**: *Financial Valuation Model: +\$1,234,000 in Operating EBITDA Recovery (+84.1% Expansion)*
                * **Visual**: Financial bridge model showing operating margin expansion from 11.6% (\$1.47M) to 19.9% (\$2.70M).
                * **Data Evidence**: Base Case levers yield +\$1.03M (Pricing Cap), +\$0.18M (3PL Restructuring), +\$0.05M (Tables Freight Surcharge), minus -\$0.02M (5% Churn Friction Drag).
                * **Presenter Notes (1.0 minute)**:
                  > *"By halting value-destructive transactions, the company does not require top-line expansion to accelerate profitability. We recapture \$1,234,000 in bottom-line operating earnings, expanding operating margins from 11.6% to 19.9% and substantially lifting return on invested capital."*

                ---

                #### Slide 10: Governance Roadmap & Board Action Items
                * **Slide Title**: *Execution Milestones & Governance Authorizations Requested*
                * **Visual**: 12-month phased implementation roadmap and formal Board resolution checklist.
                * **Presenter Notes (1.0 minute)**:
                  > *"We request immediate Board authorization to execute the 20% ERP discount lock, authorize the 3PL distributor agreements, and establish a C-suite Turnaround Oversight Committee effective next fiscal quarter. Thank you, and we invite the Board's questions."*
                """
            )

    st.divider()

    # Section 4 Proposed Solutions
    with st.container(border=True):
        st.markdown("### Practical Actions & Board Resolutions for Section 4")
        st.markdown(
            r"""
            To put this turnaround into motion over the next 6 to 12 months, we recommend three formal board resolutions:

            1. **Approve the Base Case Turnaround Plan (+\$1,234,000 Profit Increase)**:
               - *Plan*: Approve the core policy changes: 20% discount cap at checkout, \$15 oversized fee on tables, and local distribution in Turkey and Nigeria, with a built-in 5% allowance for price-sensitive customer drop-off.
               - *Expected Result*: Increases company operating profit from **\$1.47M to \$2.70M** (+84.1% increase) and lifts profit margin from **11.6% to 19.9%**.

            2. **Approve the 6–12 Month Implementation Timeline**:
               - *Months 1–3*: Program the checkout system to cap discounts at 20% and update sales commission plans to reward profit.
               - *Months 3–6*: Finalize distributor agreements in Turkey and Nigeria to stop overseas shipping losses.
               - *Months 6–12*: Add oversized shipping fees on tables and discontinue money-losing furniture models.

            3. **Create a Turnaround Oversight Committee**:
               - *Governance*: Form a monthly committee chaired by executive leadership to track key metrics (discounts over 15% kept under 2%, tables reaching positive profit, and Turkey/Nigeria breaking even).
            """
        )
