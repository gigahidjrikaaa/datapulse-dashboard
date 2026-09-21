"""Section 2 View: Geographic & Product Margin Variance (Task 2)."""

import pandas as pd
import streamlit as st

from src.components.charts import (
    create_country_loss_chart,
    create_market_share_pie,
    create_region_margin_chart,
    create_segment_performance_chart,
    create_subcat_profit_chart,
    create_territory_quadrant_chart,
)
from src.components.narratives import render_chart_story_card, render_data_dictionary_expander
from src.services.analyzer import (
    analyze_geographic_drilldown,
    analyze_product_breakdown,
    compute_territory_quadrant_matrix,
)


def render_eda_view(df: pd.DataFrame) -> None:
    """Render Section 2: Geographic & Product Margin Variance Analysis."""
    st.markdown("## Section 2: Geographic & Product Margin Variance")
    st.markdown(
        "**Diagnostic Objective**: Deconstruct performance across Geographic Hierarchies (Market → Region → Country), Merchandise Segments (Category → Sub-Category), and Client Account Tiers to isolate structural operating deficits."
    )
    st.markdown("---")

    # Formal Problem Formulation (Task 2)
    with st.container(border=True):
        st.markdown("### Formal Problem Formulation: Multi-Dimensional Margin Variance Deconstruction")
        st.markdown(
            r"""
            **Context & Stakeholder Dilemma (Task 2 Brief)**:
            Given that enterprise gross invoiced revenue expanded by +90.3%, corporate operating margin stagnation (stuck at 11.6%) implies severe internal profit dilution.
            The Chief Strategy Officer requires an empirical deconstruction across three core operational dimensions to isolate the exact locus of capital destruction:

            1. **Geographic Hierarchy Variance**: $\text{Market} \rightarrow \text{Region} \rightarrow \text{Country}$
               $$\text{Identify sovereign jurisdictions } j \in J \text{ where } \text{Profit}_j < 0 \quad \text{and quantify aggregate deficit: } \sum_{j, \text{Profit}_j < 0} \text{Profit}_j$$
            2. **Merchandise Portfolio Contribution**: $\text{Category} \rightarrow \text{Sub-Category}$
               $$\text{Differentiate Volume Shortfalls vs. Margin Realization Failures: } \text{Identify lines where } \text{Sales} \gg 0 \text{ but } \frac{\text{Profit}}{\text{Sales}} < 0$$
            3. **Customer Account Tier Homogeneity**: $\text{Segment} \in \{\text{Consumer}, \text{Corporate}, \text{Home Office}\}$
               $$\text{Test hypothesis: } \text{Margin}_{\text{Consumer}} \approx \text{Margin}_{\text{Corporate}} \approx \text{Margin}_{\text{Home Office}}$$
            """
        )

    render_data_dictionary_expander()

    if df.empty:
        st.warning("No records match the current parameter selection.")
        return

    # Direct Diagnostic Answers
    with st.container(border=True):
        st.markdown("### Executive Diagnostic: Variance Concentration")
        st.markdown(
            """
            * **Which geographic markets, operating regions, and sovereign countries exhibit structural margin deficits?**
              - The **EMEA Operating Theater** produces the lowest margin among major international units at **5.45%** (\\$43.9K profit on \\$806K sales).
              - **Territories with the Largest Operating Deficits**:
                1. **Turkey**: **-\\$98,447 net operating deficit** on \\$108.5K sales (**-90.73% margin**, average discount rate: 60.0%).
                2. **Nigeria**: **-\\$80,751 net operating deficit** on \\$54.4K sales (**-148.57% margin**, average discount rate: 70.0%).
                3. **Netherlands**: **-\\$41,070 net operating deficit** on \\$77.5K sales (**-52.98% margin**, average discount rate: 48.2%).
                4. **Honduras**: **-\\$29,482 net operating deficit** on \\$90.1K sales (**-32.71% margin**, average discount rate: 40.7%).
            * **Which merchandise divisions and sub-categories generate structural deficits? Is this a volume shortfall or a margin realization failure?**
              - **Tables** constitutes the **sole net deficit sub-category** within the global merchandise portfolio, incurring **-\\$64,083 in cumulative losses** on \\$757,042 in sales (-8.46% margin).
              - **This is strictly a margin realization failure, not a volume deficiency**: Tables generated strong commercial volume (\\$757K revenue, 3,083 units across 861 order lines). Uncontrolled promotional discounting (averaging 29.1%) combined with high freight packaging volume produced negative unit contribution on each sale.
            * **Where are enterprise operating losses concentrated?**
              - The top 10 deficit territories account for over **-\\$355,000 in net cash drain**.
            """
        )

    st.divider()

    tab_quadrant, tab_geo, tab_prod, tab_segment, tab_loss_table = st.tabs(
        [
            "Strategic Portfolio Matrix (147 Operating Territories)",
            "Geographic Market & Country Variance",
            "Product Category & Sub-Category Contribution",
            "Customer Segment Account Tier Economics",
            "Forensic Audit: Negative-Margin Transactions",
        ]
    )

    # 1. Advanced Feature: Strategic Portfolio Matrix (147 Operating Territories)
    with tab_quadrant:
        with st.container(border=True):
            st.markdown("### Strategic Portfolio Matrix: 147 Sovereign Operating Territories")
            st.markdown(
                "Multi-dimensional BCG/McKinsey strategic portfolio segmentation evaluating all 147 operating territories "
                "by commercial volume, operating profit margin, and order frequency."
            )

            quad_df = compute_territory_quadrant_matrix(df)
            quad_chart = create_territory_quadrant_chart(quad_df)
            st.plotly_chart(quad_chart, use_container_width=True)

            render_chart_story_card(
                title="Strategic Classification of 147 Operating Territories",
                what_it_shows=(
                    "2x2 strategic bubble matrix plotting sovereign territories across Gross Sales Volume ($ USD, Log Scale, X-axis) "
                    "and Operating Profit Margin (%, Y-axis). Bubble diameter reflects transaction volume. "
                    "Dashed red line demarcates break-even (0.0% margin); dotted green line indicates institutional target (10.0% margin)."
                ),
                key_takeaway=(
                    "Global operations segment into four discrete strategic profiles: "
                    "1. Core Value Engines (Green): High volume, high margin markets (US, UK, Germany, Australia, China, India). "
                    "2. Margin-Diluted Volume Channels (Amber): Large sales scale but sub-par margins (France, Philippines, Mexico). "
                    "3. High-Yield Niche Centers (Blue): Moderate sales volume generating superior margins >15% (Canada, New Zealand, Norway). "
                    "4. Deficit Rationalization Priorities (Red): Chronic capital drains operating below break-even (Turkey, Nigeria, Netherlands, Honduras)."
                ),
                business_impact=(
                    "The Board should avoid broad corporate mandate blanket cuts. Capital, promotional budgets, and inventory allocation "
                    "must be differentiated: invest aggressively in Core Engines and Niche Centers, renegotiate commercial pricing in Diluted Channels, "
                    "and restructure delivery models in Deficit Priorities."
                ),
                recommendation=(
                    "Establish a two-tier governance framework: grant localized pricing flexibility only to Core Engines and Niche Centers; "
                    "strip localized pricing discretion from Deficit Territories."
                ),
            )

        st.divider()

        with st.container(border=True):
            st.markdown("#### Portfolio Quadrant Summary Matrix")
            quad_summary = (
                quad_df.groupby("Portfolio_Quadrant", as_index=False)
                .agg(
                    Territories=("Country", "count"),
                    Total_Sales=("Sales", "sum"),
                    Total_Profit=("Profit", "sum"),
                    Avg_Discount=("Avg_Discount_Pct", "mean"),
                )
            )
            quad_summary["Operating_Margin"] = (
                quad_summary["Total_Profit"] / quad_summary["Total_Sales"].replace(0, float("nan"))
            ).fillna(0.0) * 100.0

            st.dataframe(
                quad_summary.style.format(
                    {
                        "Territories": "{:,}",
                        "Total_Sales": "${:,.2f}",
                        "Total_Profit": "${:,.2f}",
                        "Operating_Margin": "{:.2f}%",
                        "Avg_Discount": "{:.1f}%",
                    }
                ),
                use_container_width=True,
            )

    # 2. Geographic Drilldown
    with tab_geo:
        mkt_df, reg_df, country_df = analyze_geographic_drilldown(df)

        c1, c2 = st.columns([3, 2])
        with c1:
            with st.container(border=True):
                st.markdown("#### Primary Operating Deficit Territories")
                loss_chart = create_country_loss_chart(country_df, bottom_n=10)
                st.plotly_chart(loss_chart, use_container_width=True)

                render_chart_story_card(
                    title="Sovereign Territory Margin Deficits (Turkey, Nigeria, Netherlands)",
                    what_it_shows=(
                        "Ranking of the bottom 10 sovereign operating territories by cumulative negative operating profit. "
                        "Red bars delineate the absolute dollar deficit incurred in each jurisdiction."
                    ),
                    key_takeaway=(
                        "Deficits are acutely concentrated: Turkey (-$98.4K on $108.5K sales) and Nigeria (-$80.8K on $54.4K sales) "
                        "demonstrate extreme negative operating margins (-90.7% and -148.6%). Together, these two jurisdictions destroy $179K in capital, "
                        "driven by standard baseline discounts ranging between 60.0% and 70.0%."
                    ),
                    business_impact=(
                        "The enterprise's centralized commercial pricing framework fails in volatile or high-tariff international markets. "
                        "Local sales teams utilized high discount allowances to win volume quotas, while the corporate center absorbed "
                        "international freight charges and import clearance duties."
                    ),
                    recommendation=(
                        "Immediately suspend standard discount authority in Turkey, Nigeria, and the Netherlands. "
                        "Transition international fulfillment from direct cross-border shipment to localized third-party distribution (3PL) models."
                    ),
                )

        with c2:
            with st.container(border=True):
                st.markdown("#### Market Sales Proportions")
                pie_chart = create_market_share_pie(mkt_df)
                st.plotly_chart(pie_chart, use_container_width=True)

                render_chart_story_card(
                    title="Geographic Revenue Distribution and Regional Margin Disparities",
                    what_it_shows="Proportional sales volume across the seven primary geographic operating theaters.",
                    key_takeaway=(
                        "APAC ($3.59M, 28.4%), EU ($2.94M, 23.2%), and US ($2.30M, 18.2%) represent 69.8% of global volume with stable "
                        "operating margins (~12.2% to 12.7%). Conversely, EMEA ($806K, 6.4%) generates a severely depressed 5.45% margin."
                    ),
                    business_impact="Core mature operating units are commercially sound; regional deficits in EMEA and Africa dilute group return on equity.",
                    recommendation="Safeguard commercial margins in primary theaters while executing operational restructuring across EMEA and Africa.",
                )

        st.divider()

        # Region-level hierarchy (fills the reg_df gap)
        with st.container(border=True):
            st.markdown("#### Sub-Regional Operating Profit & Margin Breakdown (13 Geographic Regions)")
            st.markdown(
                "Hierarchical deconstruction from Market to Sub-Region, evaluating margin realization across operating clusters."
            )
            col_reg_chart, col_reg_table = st.columns([3, 2])
            with col_reg_chart:
                reg_fig = create_region_margin_chart(reg_df)
                st.plotly_chart(reg_fig, use_container_width=True)
            with col_reg_table:
                st.markdown("##### Sub-Region Operating Summary")
                st.dataframe(
                    reg_df.style.format(
                        {
                            "Sales": "${:,.2f}",
                            "Profit": "${:,.2f}",
                            "Shipping_Cost": "${:,.2f}",
                            "Profit_Margin": "{:.2f}%",
                            "Avg_Discount_Pct": "{:.1f}%",
                            "Orders": "{:,}",
                        }
                    ),
                    use_container_width=True,
                )

        st.divider()

        with st.container(border=True):
            st.markdown("#### Primary Theater Operating Matrix (Markets)")
            st.dataframe(
                mkt_df.style.format(
                    {
                        "Sales": "${:,.2f}",
                        "Profit": "${:,.2f}",
                        "Shipping_Cost": "${:,.2f}",
                        "Profit_Margin": "{:.2f}%",
                        "Avg_Discount_Pct": "{:.1f}%",
                        "Orders": "{:,}",
                    }
                ),
                use_container_width=True,
            )

        # Full Country-Level Table (All 147 Territories)
        with st.expander("Explore Full Sovereign Territories Operating Matrix (All 147 Countries)"):
            st.markdown(
                "Comprehensive operating ledger across all 147 sovereign operating jurisdictions, sorted by cumulative operating contribution."
            )
            st.dataframe(
                country_df.style.format(
                    {
                        "Sales": "${:,.2f}",
                        "Profit": "${:,.2f}",
                        "Shipping_Cost": "${:,.2f}",
                        "Profit_Margin": "{:.2f}%",
                        "Avg_Discount_Pct": "{:.1f}%",
                        "Orders": "{:,}",
                    }
                ),
                use_container_width=True,
            )

    # 3. Product Drilldown
    with tab_prod:
        cat_df, subcat_df = analyze_product_breakdown(df)

        with st.container(border=True):
            st.markdown("#### Merchandise Line Profitability Distribution")
            subcat_chart = create_subcat_profit_chart(subcat_df)
            st.plotly_chart(subcat_chart, use_container_width=True)

            render_chart_story_card(
                title="Portfolio Contribution Variance: Tables Merchandise Line Deficit",
                what_it_shows=(
                    "Horizontal diverging bar chart comparing all 17 portfolio merchandise lines. "
                    "Green indicates positive net operating contribution; red highlights net deficit lines (Tables)."
                ),
                key_takeaway=(
                    "Technology lines (Copiers +$258.6K, Phones +$216.7K, Accessories +$129.6K) and Office Supplies (Storage +$108.5K, Binders +$72.4K) "
                    "deliver robust profitability. Tables is the sole net deficit line (-$64,083 loss) despite generating $757K in top-line sales."
                ),
                business_impact=(
                    "Tables is an operational pricing failure. Heavy dimensional packaging elevates freight-to-value ratios. "
                    "Granting 29.1% average promotional discounts on bulky merchandise systematically eliminates unit gross margin."
                ),
                recommendation=(
                    "Restructure the Tables commercial catalog: introduce mandatory dimensional freight surcharges on commercial deliveries, "
                    "raise base catalog pricing, and cap promotional allowances at 10%."
                ),
            )

        st.divider()

        col_cat, col_subcat = st.columns(2)
        with col_cat:
            with st.container(border=True):
                st.markdown("##### Performance by Merchandise Division")
                st.dataframe(
                    cat_df.style.format(
                        {
                            "Sales": "${:,.2f}",
                            "Profit": "${:,.2f}",
                            "Profit_Margin": "{:.2f}%",
                            "Avg_Discount_Pct": "{:.1f}%",
                            "Quantity": "{:,}",
                        }
                    ),
                    use_container_width=True,
                )

        with col_subcat:
            with st.container(border=True):
                st.markdown("##### Sub-Categories Ranked by Operating Contribution")
                st.dataframe(
                    subcat_df.style.format(
                        {
                            "Sales": "${:,.2f}",
                            "Profit": "${:,.2f}",
                            "Profit_Margin": "{:.2f}%",
                            "Avg_Discount_Pct": "{:.1f}%",
                            "Quantity": "{:,}",
                        }
                    ),
                    use_container_width=True,
                )

    # 4. Customer Segment Drilldown
    with tab_segment:
        with st.container(border=True):
            st.markdown("#### Customer Account Tier Economic Comparison")
            segment_df = (
                df.groupby("Segment", as_index=False)
                .agg(
                    Sales=("Sales", "sum"),
                    Profit=("Profit", "sum"),
                    Orders=("Order ID", "nunique"),
                    Avg_Discount=("Discount", "mean"),
                )
            )
            segment_df["Profit_Margin"] = (segment_df["Profit"] / segment_df["Sales"]) * 100.0
            segment_df["Avg_Discount_Pct"] = segment_df["Avg_Discount"] * 100.0

            segment_chart = create_segment_performance_chart(segment_df)
            st.plotly_chart(segment_chart, use_container_width=True)

            st.markdown("##### Account Tier Economic Matrix")
            st.dataframe(
                segment_df.style.format(
                    {
                        "Sales": "${:,.2f}",
                        "Profit": "${:,.2f}",
                        "Profit_Margin": "{:.2f}%",
                        "Avg_Discount_Pct": "{:.1f}%",
                        "Orders": "{:,}",
                    }
                ),
                use_container_width=True,
            )

            render_chart_story_card(
                title="Customer Account Tier Uniformity (Non-Explanatory Factor)",
                what_it_shows="Financial performance across Consumer, Corporate, and Home Office purchasing classifications.",
                key_takeaway=(
                    "All three customer account tiers display near-identical operating margins: Consumer (11.51%), Corporate (11.54%), "
                    "and Home Office (11.99%), with average discount rates clustered tightly between 14.1% and 14.4%."
                ),
                business_impact=(
                    "This finding confirms that enterprise underperformance is not driven by customer segmentation. "
                    "Client classifications generate comparable returns under standardized pricing. The operational defect resides strictly in geographic and product pricing rules."
                ),
                recommendation="Retain existing commercial go-to-market segmentation; concentrate executive interventions on pricing authority and fulfillment logistics.",
            )

    # 5. Detailed Loss Orders Inspector
    with tab_loss_table:
        with st.container(border=True):
            st.markdown("#### Forensic Transaction Audit: Negative-Margin Order Lines")
            loss_df = df[df["Profit"] < 0].sort_values(by="Profit", ascending=True)

            st.write(
                f"Displaying **{len(loss_df):,}** order transactions executed below cost-to-serve."
            )

            display_cols = [
                "Order ID",
                "Order Date",
                "Country",
                "City",
                "Sub-Category",
                "Product Name",
                "Sales",
                "Discount",
                "Shipping Cost",
                "Profit",
            ]
            st.dataframe(
                loss_df[display_cols].head(100).style.format(
                    {
                        "Sales": "${:,.2f}",
                        "Discount": "{:.1%}",
                        "Shipping Cost": "${:,.2f}",
                        "Profit": "${:,.2f}",
                    }
                ),
                use_container_width=True,
            )

            csv_loss = loss_df[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Negative-Margin Audit Records (CSV)",
                data=csv_loss,
                file_name="global_superstore_negative_margin_transactions.csv",
                mime="text/csv",
            )

    st.divider()

    # Section 2 Proposed Solutions
    with st.container(border=True):
        st.markdown("### Section 2: Strategic Proposed Solutions")
        st.markdown(
            r"""
            Based on the multi-dimensional variance diagnostic, the strategic taskforce recommends three operational solutions:

            1. **Restructure Sovereign Deficit Channels (Turkey, Nigeria, Netherlands, Honduras)**:
               - *Operational Action*: Immediately terminate direct cross-border corporate fulfillment into Turkey (-\$98.4K deficit, -90.7% margin) and Nigeria (-\$80.8K deficit, -148.6% margin). Transition these accounts to bonded in-country third-party logistics (3PL) master distributors with wholesale transfer pricing indexed to hard currencies.
               - *Financial Recovery*: **Eliminates +\$179,198 in direct bilateral deficits** (and up to +\$249,750 across all top-4 deficit territories).

            2. **Merchandise Portfolio Turnaround: Tables Catalog Restructuring**:
               - *Operational Action*: Tables represents a margin realization failure (-\$64K loss on \$757K sales), not a demand failure. Restructure the commercial furniture line: introduce mandatory dimensional freight surcharges, eliminate unapproved commercial discounts, and discontinue negative-margin SKUs.
               - *Financial Recovery*: **+\$46,245 bulky freight recovery and +\$80,000+ margin turnaround**, converting Tables from enterprise loss-maker into positive contribution margin.

            3. **Preserve Customer Account Tier Segmentation Structure**:
               - *Operational Action*: Retain the existing sales organizational alignment across Consumer, Corporate, and Home Office. The data confirms near-identical margins (~11.5%) across all three account tiers, demonstrating that account classification is commercially sound and not the cause of margin dilution.
            """
        )
