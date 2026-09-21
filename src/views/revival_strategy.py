"""Section 4 View: Strategic Turnaround Framework & Board Presentation Deck (Task 4 & 5)."""

import pandas as pd
import streamlit as st

from src.components.charts import create_ebitda_bridge_chart
from src.components.metrics import render_kpi_card
from src.components.narratives import render_chart_story_card, render_data_dictionary_expander
from src.services.analyzer import (
    compute_scenario_sensitivity_matrix,
    simulate_turnaround_impact,
)



def render_revival_strategy_view(df: pd.DataFrame | None = None) -> None:
    """Render Section 4: Strategic Turnaround Framework, What-If Policy Simulator, and Board Presentation Deck."""
    st.markdown("## Section 4: Strategic Turnaround Framework & Board Presentation Deck")
    st.markdown(
        "**Strategic Objective**: Formulate three prioritized turnaround initiatives with executive ownership, implementation timelines, KPIs, and financial recovery models, alongside an interactive what-if policy simulator and an 8–10 slide presentation deck structured for the Board of Directors."
    )
    st.markdown("---")

    # Formal Problem Formulation (Tasks 4 & 5)
    with st.container(border=True):
        st.markdown("### Formal Problem Formulation: Strategic Turnaround Optimization & Governance Architecture")
        st.markdown(
            r"""
            **Context & Stakeholder Mandate (Tasks 4 & 5 Brief)**:
            The Chief Strategy Officer and Analytics Taskforce are chartered by the Board of Directors to transition from forensic diagnostic to actionable turnaround execution.
            The mandate requires solving a multi-variable corporate optimization problem:

            1. **Turnaround Optimization Model**: Maximize net operating EBITDA while penalizing customer churn elasticity:
               $$\max_{\delta_{\text{cap}}, \tau, s} \text{EBITDA} = \text{EBITDA}_{\text{base}} + \Delta \Pi_{\text{pricing}}(\delta_{\text{cap}}) + \Delta \Pi_{\text{geo}}(\tau) + \Delta \Pi_{\text{freight}}(s) - \text{ChurnDrag}(\epsilon)$$
               - $\delta_{\text{cap}}$: Maximum allowable commercial discount ceiling (ERP hard cap).
               - $\tau$: Binary restructuring vector converting deficit territories (Turkey, Nigeria) to 3PL distributor models.
               - $s$: Dimensional freight surcharge ($/unit) levied on bulky merchandise lines (Tables).
               - $\epsilon$: Price elasticity churn coefficient modeling customer attrition on repriced transactions.
            2. **Executive Accountability & Governance Architecture**:
               - Establish discrete C-suite and VP ownership for each intervention.
               - Sequence operational milestones into a 6–12 month phased implementation roadmap.
               - Deliver a cohesive 10-slide executive briefing deck calibrated for Board of Directors deliberation.
            """
        )

    render_data_dictionary_expander()

    if df is None or df.empty:
        df = st.session_state.get("filtered_df")

    # Primary Feature: Interactive What-If Turnaround Policy Simulator & EBITDA Bridge
    if df is not None and not df.empty:
        st.markdown("### Interactive What-If Turnaround Policy Simulator & EBITDA Bridge")
        st.markdown(
            "Dynamic decision modeling engine evaluating the bottom-line financial impact of key turnaround policy levers against historical transaction baselines. "
            "Adjust pricing governance ceilings, international distribution models, freight surcharges, and customer churn elasticity to evaluate simulated operating EBITDA."
        )

        with st.container():
            sim_col1, sim_col2 = st.columns(2)

            with sim_col1:
                st.markdown("#### Commercial Pricing & Elasticity Levers")
                max_discount_cap_pct = st.slider(
                    "Contractual Discount Ceiling (%)",
                    min_value=10.0,
                    max_value=30.0,
                    value=20.0,
                    step=1.0,
                    help="Programmatic ERP cap on maximum allowable commercial discounts. Transactions exceeding this threshold are repriced at the ceiling rate.",
                )
                volume_attrition_rate_pct = st.slider(
                    "Customer Churn Friction Sensitivity (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=5.0,
                    step=1.0,
                    help="Simulated percentage order attrition among commercial accounts affected by discount capping due to price elasticity.",
                )

            with sim_col2:
                st.markdown("#### Logistics & Operational Restructuring Levers")
                table_freight_surcharge = st.slider(
                    "Tables Dimensional Freight Surcharge ($/Unit)",
                    min_value=0.0,
                    max_value=50.0,
                    value=15.0,
                    step=5.0,
                    help="Mandatory carrier freight pass-through surcharge levied on bulky table units to recover packaging and volumetric freight deficits.",
                )
                restructure_deficit_territories = st.toggle(
                    "Restructure Sovereign Deficit Territories (Turkey & Nigeria 3PL Model)",
                    value=True,
                    help="Transition volatile, high-tariff international operations (Turkey and Nigeria) to localized bonded 3PL master distributor models, eliminating structural cross-border delivery subsidies.",
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
        st.plotly_chart(w_chart, use_container_width=True)

        render_chart_story_card(
            title="Strategic EBITDA Bridge: Financial Value Creation Dynamics",
            what_it_shows=(
                "Plotly Waterfall chart illustrating step-by-step EBITDA bridge progression: starting from historical baseline operating profit, "
                "adding pricing discipline recovery, international 3PL restructuring, and bulky freight recovery, "
                "deducting simulated customer volume churn friction, and arriving at projected turnaround EBITDA."
            ),
            key_takeaway=(
                f"Under the selected configuration (Discount Cap: {max_discount_cap_pct:.0f}%, Churn Friction: {volume_attrition_rate_pct:.0f}%, "
                f"Table Surcharge: ${table_freight_surcharge:.0f}, 3PL Restructuring: {'Enabled' if restructure_deficit_territories else 'Disabled'}), "
                f"Global Superstore unlocks +${sim_results['net_ebitda_uplift']:,.0f} in operating profit, expanding operating margin from "
                f"{sim_results['baseline_margin']:.1f}% to {sim_results['projected_margin']:.1f}%."
            ),
            business_impact=(
                "Crucially, the financial model proves that turnaround viability does not require risky top-line revenue acceleration. "
                "Eliminating structural pricing leakage and logistics subsidies captures immediate earnings expansion even when factoring "
                "in customer volume churn penalties."
            ),
            recommendation=(
                "Present this sensitivity bridge to the Board of Directors as empirical justification for enforcing the 20% discount lock "
                "and renegotiating international distributor agreements."
            ),
        )

        st.markdown("#### Turnaround Financial Bridge Breakdown")
        bridge_df = pd.DataFrame(
            [
                {
                    "Strategic Value Driver": "1. Baseline Historical Operating Profit",
                    "Impact ($ USD)": sim_results["baseline_profit"],
                    "Mechanism": "Reported enterprise operating earnings prior to intervention.",
                },
                {
                    "Strategic Value Driver": f"2. Pricing Governance Recovery (Cap at {max_discount_cap_pct:.0f}%)",
                    "Impact ($ USD)": sim_results["pricing_recovery"],
                    "Mechanism": f"Re-pricing {sim_results['affected_orders_count']:,} transactions where discounts exceeded {max_discount_cap_pct:.0f}%.",
                },
                {
                    "Strategic Value Driver": "3. Sovereign 3PL Restructuring (Turkey & Nigeria)",
                    "Impact ($ USD)": sim_results["territory_recovery"],
                    "Mechanism": "Transition to local in-country master distributors, eliminating cross-border delivery deficits.",
                },
                {
                    "Strategic Value Driver": f"4. Bulky Merchandise Freight Pass-Through (${table_freight_surcharge:.0f}/unit)",
                    "Impact ($ USD)": sim_results["table_freight_recovery"],
                    "Mechanism": "Dimensional freight surcharge on Tables to recover carrier oversized shipping expenses.",
                },
                {
                    "Strategic Value Driver": f"5. Customer Volume Churn Elasticity Drag ({volume_attrition_rate_pct:.0f}%)",
                    "Impact ($ USD)": -sim_results["attrition_drag"],
                    "Mechanism": "Conservative allowance for customer attrition among accounts losing discount privileges.",
                },
                {
                    "Strategic Value Driver": "6. Net Simulated Operating EBITDA",
                    "Impact ($ USD)": sim_results["projected_profit"],
                    "Mechanism": f"Target operating profit under modeled turnaround policy (Margin: {sim_results['projected_margin']:.2f}%).",
                },
            ]
        )
        st.dataframe(
            bridge_df.style.format({"Impact ($ USD)": "${:,.2f}"}),
            use_container_width=True,
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
            use_container_width=True,
        )

    st.divider()

    # 1. The Three Priority Actions
    st.markdown("### Three Prioritized Turnaround Initiatives")

    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        with st.container(border=True):
            st.markdown(
                """
                #### Initiative 1: Pricing Governance
                * **Underlying Root Cause**: Unregulated price concessions exceeding the 20.0% threshold, causing -\\$814,682 in operating losses.
                * **Executive Owner**: Chief Commercial Officer (CCO) & VP of Global Sales Operations.
                * **Implementation Timeline**: Months 1 through 3.
                * **Operational Mechanism**:
                  - Configure ERP software to reject discounts > 15.0% without automated VP authorization.
                  - Programmatically lock transaction processing for discounts > 20.0%.
                  - Restructure commercial sales incentive scorecards to reward Gross Margin Contribution rather than gross top-line volume.
                * **Key Performance Indicators (KPIs)**:
                  - Share of orders with discount > 15.0% (Target: < 2.0%)
                  - Global weighted-average discount rate (Target: < 12.0%)
                  - Sales division contribution margin (Target: > 15.0%)
                * **Expected Financial Impact**:
                  - **Recovers +\\$450,000 to +\\$600,000 in annualized operating profit**.
                  - Eliminates 80.0% of negative-margin transactions within 90 days.
                """
            )

    with action_col2:
        with st.container(border=True):
            st.markdown(
                """
                #### Initiative 2: Regional Logistics Restructuring
                * **Underlying Root Cause**: Cross-border fulfillment expenses exceeding realized net revenue in volatile, high-tariff jurisdictions (Turkey, Nigeria).
                * **Executive Owner**: VP of Global Supply Chain & Regional Managing Directors.
                * **Implementation Timeline**: Months 3 through 6.
                * **Operational Mechanism**:
                  - Discontinue direct cross-border expedited air fulfillment into Nigeria and Turkey.
                  - Establish partnerships with in-country master distributors and bonded third-party logistics (3PL) warehousing providers.
                  - Index localized pricing catalogs to hard currencies or dynamic local inflation benchmarks.
                * **Key Performance Indicators (KPIs)**:
                  - Country-level operating margin (Target: Break-even within 90 days; > 8.0% within 12 months)
                  - Landed freight cost ratio (Target: < 12.0% of invoiced sales)
                * **Expected Financial Impact**:
                  - **Eliminates -\\$220,000 in persistent annual cash drain**.
                  - Restores regional operating margins in EMEA and Africa to institutional benchmarks.
                """
            )

    with action_col3:
        with st.container(border=True):
            st.markdown(
                """
                #### Initiative 3: Bulky Freight Pass-Through
                * **Underlying Root Cause**: Tables portfolio deficit (-\\$64,083 loss) driven by dimensional packaging volume and unrecovered freight.
                * **Executive Owner**: Head of Product Merchandising & Director of Logistics Pricing.
                * **Implementation Timeline**: Months 6 through 12.
                * **Operational Mechanism**:
                  - Discontinue negative-contribution SKUs within the Tables and bulky Furniture line.
                  - Implement mandatory dimensional freight surcharges: pass oversize carrier handling expenses to commercial B2B buyers.
                  - Introduce flat-pack product alternatives to reduce volumetric shipping footprint.
                * **Key Performance Indicators (KPIs)**:
                  - Tables sub-category operating profit (Target: > +\\$50,000)
                  - Dimensional freight recovery compliance (Target: 100.0%)
                * **Expected Financial Impact**:
                  - **+\\$80,000 annualized margin turnaround on bulky merchandise**, converting Tables into a positive contributor.
                """
            )

    st.divider()

    # 2. 6-12 Month Implementation Milestones
    with st.container(border=True):
        st.markdown("### 6–12 Month Strategic Implementation Roadmap")
        st.markdown(
            """
            | Implementation Phase | Milestone / Operational Deliverable | Target Timeline | Governance Target |
            | :--- | :--- | :--- | :--- |
            | **Phase 1: Commercial Control & Contract Alignment** | Implement programmatic 20% discount lock in ERP software. Transition commercial commission contracts to Gross Margin Contribution. | Months 1–2 | Zero unapproved orders processed with discount > 20.0%. |
            | **Phase 2: International Distribution Restructuring** | Suspend unhedged standard discounting in Turkey and Nigeria. RFP local 3PL warehousing and in-country master distributor partners. | Months 3–4 | Regional operating losses reduced by 70.0%; freight expense reduced by \\$150K. |
            | **Phase 3: Merchandise Pricing & Freight Recovery** | Reprice Tables and bulky Furniture; enforce dimensional freight pass-through surcharges on commercial deliveries. | Months 5–7 | Tables sub-category achieves monthly operating break-even. |
            | **Phase 4: Institutional Review & Margin Optimization** | Conduct comprehensive quarterly margin audits across all 147 operating territories. Institutionalize corporate pricing committee. | Months 8–12 | Consolidated enterprise operating margin expands from 11.6% to **> 15.5%**. |
            """
        )

    st.divider()

    # # 3. Presentation Deck Outline (8-10 Slides)
    # with st.container(border=True):
    #     st.markdown("### Board of Directors Presentation Deck Outline (10-Minute Executive Session)")
    #     st.markdown(
    #         "Structured slide-by-slide executive briefing designed for a formal 10-minute board presentation followed by 5 minutes of strategic Q&A:"
    #     )

    #     with st.expander("Executive Deck Architecture: Slide Content, Visual Evidence & Presenter Notes", expanded=True):
    #         st.markdown(
    #             """
    #             #### Slide 1: Executive Title & Diagnostic Scope
    #             * **Slide Title**: *Global Superstore: Strategic Performance Evaluation & Turnaround Plan*
    #             * **Subtitle**: *Unlocking \\$920,000 in Operating EBITDA Through Commercial Discipline & Operating Model Restructuring*
    #             * **Presenters**: Special Strategy & Operations Taskforce
    #             * **Visual**: Institutional executive title card with FY2011–FY2014 headline audit metrics.
    #             * **Presenter Notes (1.0 minute)**:
    #               > *"Members of the Board, external speculation regarding Global Superstore's revenue stagnation is empirically disproven by transaction data. Our commercial demand engine is robust, but operating earnings are diluted by an internal pricing governance failure. Today, we present conclusive audit evidence and an operational roadmap to unlock up to \\$920,000 in bottom-line operating profit."*

    #             ---

    #             #### Slide 2: Multi-Year Revenue Audit (Refuting Market Rumors)
    #             * **Slide Title**: *Top-Line Performance: Revenue Expanded +90.3% to \\$4.30M*
    #             * **Visual**: Multi-year revenue and operating profit progression chart (FY2011–FY2014) with annual growth indicators.
    #             * **Data Evidence**: Sales scaled from \\$2.26M to \\$4.30M (+26.3% YoY in FY2014); operating profit expanded from \\$249K to \\$504K.
    #             * **Presenter Notes (1.0 minute)**:
    #               > *"Over the past four fiscal years, Global Superstore added more than \\$2.0 million in top-line revenue, expanding annual order volume from 4,440 to 8,531 orders. However, consolidated operating margin remained constrained at 11.6%, failing to capture operating leverage benefits as fixed overhead scaled."*

    #             ---

    #             #### Slide 3: The True Vulnerability: \\$920,000 in Margin Dilution
    #             * **Slide Title**: *Capital Erosion: 24.5% of Transaction Volume Executed at an Operating Loss*
    #             * **Visual**: Financial bridge chart: Gross Profitable Contribution (\\$2.39M) minus Negative Margin Drag (-\\$920K) = Reported Operating Profit (\\$1.47M).
    #             * **Data Evidence**: 12,544 order transactions executed below cost-to-serve, destroying \\$920,646 in earnings.
    #             * **Presenter Notes (1.0 minute)**:
    #               > *"This is the central vulnerability of our operating model: our profitable core generated \\$2.39 million in operating profit. However, 24.5% of order lines were executed at negative margins, destroying \\$920,000 in capital. Management has focused on gross revenue volume while permitting unmonitored profit leakage."*

    #             ---

    #             #### Slide 4: Territorial Variance Analysis (Concentration of Deficits)
    #             * **Slide Title**: *Geographic Deficits: Four Sovereign Jurisdictions Account for \\$250K in Losses*
    #             * **Visual**: Horizontal bar chart ranking operating deficits across sovereign territories (Turkey, Nigeria, Netherlands, Honduras).
    #             * **Data Evidence**: Turkey (-\\$98.4K loss, -90.7% margin), Nigeria (-\\$80.8K loss, -148.6% margin).
    #             * **Presenter Notes (1.0 minute)**:
    #               > *"Operating deficits are concentrated geographically. Turkey and Nigeria alone destroyed \\$179,000 in capital. In both territories, sales teams offered 60% to 70% baseline discounts to meet volume targets, while the corporate center absorbed cross-border logistics and customs duties in volatile currency environments."*

    #             ---

    #             #### Slide 5: Merchandise Portfolio Diagnostic (The Tables Anomaly)
    #             * **Slide Title**: *Portfolio Contribution: 16 Profitable Merchandise Lines vs. 1 Net Deficit Sub-Category*
    #             * **Visual**: Diverging bar chart displaying net operating contribution across all 17 portfolio sub-categories.
    #             * **Data Evidence**: Copiers (+\\$258.6K) and Phones (+\\$216.7K) deliver strong returns; Tables generated a cumulative deficit of -\\$64,083 on \\$757K in sales.
    #             * **Presenter Notes (1.0 minute)**:
    #               > *"Sixteen out of seventeen merchandise sub-categories are highly profitable. Tables is the sole net deficit line. This is an operational pricing failure: tables generate high freight costs due to package dimensions. Applying 29% average discounts while subsidizing freight guarantees negative unit economics."*

    #             ---

    #             #### Slide 6: Root Cause Diagnostic: The 20% Discount Inversion Bound
    #             * **Slide Title**: *Unit Economics Inversion: Operating Margins Collapse Past 20% Discount*
    #             * **Visual**: Operating margin distribution across discount brackets (0% to >50%), highlighting the break-even threshold.
    #             * **Data Evidence**: Orders discounted ≤20% generate +9.9% to +25.3% margin; orders discounted >20% destroyed -\\$814,682.
    #             * **Presenter Notes (1.5 minutes)**:
    #               > *"This is the definitive empirical finding of our audit: our gross product margin prior to discounting is 25% to 30%. Concessions up to 20% preserve positive returns. However, the moment discount rates exceed 20%, unit economics invert completely, producing cash burn on every shipment. Over \\$814,000 in profit was conceded through unmonitored discounting past this threshold."*

    #             ---

    #             #### Slide 7: Operational Blind Spots: Freight Cost Absorption & System Controls
    #             * **Slide Title**: *Operational Gaps: Unrecovered Expedited Freight & Missing IT Controls*
    #             * **Visual**: Freight absorption ratios across logistics fulfillment tiers (Same Day at 17.4% vs Standard Class at 8.1%) and governance hierarchy.
    #             * **Presenter Notes (1.0 minute)**:
    #               > *"Our legacy ERP architecture lacks automated margin validation controls, allowing sales representatives to enter transactions with 70% discounts and free expedited delivery without managerial review. We have subsidized premium carrier delivery without recovering freight surcharges."*

    #             ---

    #             #### Slide 8: The Three-Pillar Turnaround Framework
    #             * **Slide Title**: *Turnaround Strategy: Three Prioritized Interventions for Immediate Execution*
    #             * **Visual**: Structured three-pillar framework (Pricing Governance, Channel Restructuring, Bulky Freight Recovery).
    #             * **Presenter Notes (1.5 minutes)**:
    #               > *"We propose three actionable initiatives: First, establish an institutional discount ceiling at 15% with a hard 20% ERP block. Second, restructure Turkey and Nigeria into third-party distributor models. Third, implement dimensional freight surcharges across the Tables portfolio."*

    #             ---

    #             #### Slide 9: Commercial Value Creation & EBITDA Bridge
    #             * **Slide Title**: *Financial Valuation Model: +\\$920K in EBITDA Recovery Potential*
    #             * **Visual**: Financial bridge model showing operating margin expansion from 11.6% (\\$1.47M) to >15.5% (\\$2.39M).
    #             * **Presenter Notes (1.0 minute)**:
    #               > *"By halting value-destructive transactions, the company does not require top-line expansion to accelerate profitability. We recapture \\$500,000 to \\$920,000 in bottom-line operating earnings, expanding operating margins from 11.6% to over 15.5% and substantially lifting return on invested capital."*

    #             ---

    #             #### Slide 10: Governance Roadmap & Board Action Items
    #             * **Slide Title**: *Execution Milestones & Governance Authorizations Requested*
    #             * **Visual**: 12-month phased implementation roadmap and formal Board resolution checklist.
    #             * **Presenter Notes (1.0 minute)**:
    #               > *"We request immediate Board authorization to execute the 20% ERP discount lock and realign commercial sales compensation to gross margin contribution effective next fiscal quarter. Thank you, and we invite the Board's questions."*
    #             """
    #         )

    # st.divider()

    # Section 4 Proposed Solutions
    with st.container(border=True):
        st.markdown("### Section 4: Strategic Proposed Solutions & Board Action Charter")
        st.markdown(
            r"""
            To achieve sustainable corporate revival within 6 to 12 months, the strategic taskforce submits three formal resolutions for Board authorization:

            1. **Adopt the Base Case Turnaround Model (+\$684,000 Operating EBITDA Expansion)**:
               - *Policy Package*: Formally authorize the Base Case turnaround parameters: 20.0% contractual discount ceiling, \$15/unit bulky table pass-through surcharge, and full bonded 3PL transition across Turkey and Nigeria, absorbing a conservative 5.0% customer churn friction buffer.
               - *Financial Yield*: Expands consolidated operating profit from **\$1.47M to \$2.15M** (+46.5% earnings expansion) and elevates operating margin from **11.6% to 16.5%**.

            2. **Authorize the 6–12 Month Phased Implementation Roadmap**:
               - *Phase I (Months 1–3)*: Hardcode programmatic ERP discount locks (<15% standard sales rep discretion, 15–20% automated VP sign-off, >20% hard block) and transition sales scorecards to contribution margin.
               - *Phase II (Months 3–6)*: Execute 3PL master distributor agreements in Turkey and Nigeria; transition fulfillment from cross-border air to localized bonded maritime distribution.
               - *Phase III (Months 6–12)*: Implement dimensional freight surcharges across the Tables catalog and prune chronically negative-margin furniture SKUs.

            3. **Charter the Board Turnaround Oversight Committee**:
               - *Governance Mandate*: Establish a bi-weekly C-suite Turnaround Steering Committee chaired by the CSO and CFO to audit monthly operational scorecards (Discount Leakage Rate < 2.0%, Tables Operating Margin > +10%, Deficit Territory Break-Even).
            """
        )
