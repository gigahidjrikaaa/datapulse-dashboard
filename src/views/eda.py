"""Chapter 2 View: Where It Leaks - Geographic & Product Margin Variance (Task 2)."""

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
from src.components.story import render_story_ribbon
from src.services.analyzer import (
    analyze_geographic_drilldown,
    analyze_product_breakdown,
    compute_territory_quadrant_matrix,
)


def render_eda_view(df: pd.DataFrame) -> None:
    """Render Chapter 2: the geographic and product drilldown behind the losses."""
    render_story_ribbon(
        "ch2",
        "The damage is concentrated, not general. Three quarters of orders are healthy - the losses trace to "
        "four countries led by Turkey (-$98K) and Nigeria (-$81K), exactly one product line (Tables, -$64K), and "
        "one weak market (EMEA at 5.4% margin). Fix the tail and the company is fine.",
        "Ch. 3 - Why It Happens: We Gave It Away Past 20%",
    )
    st.markdown("## Chapter 2 - Where It Leaks: Four Countries, One Product, One Market")
    st.markdown(
        "**The claim this chapter defends**: the losses are not spread across the business - they sit in "
        "nameable places. Drilling Market → Region → Country and Category → Sub-Category, plus customer "
        "segments, shows the health of the core and names the exact territories and products that drain it."
    )
    st.markdown("---")

    # Core Business Problem & Key Questions
    with st.container(border=True):
        st.markdown("### The Core Question: Where Are the Biggest Profit Leaks?")
        st.markdown(
            """
            **What we're investigating**:
            Even though sales grew +90.3%, our overall profit margin stayed stuck at 11.6%. That means internal losses are eating up the extra profit.
            To find where that money went, we break down the numbers across three areas:

            1. **By Country & Region**: Which countries are making healthy profits, and which ones are losing money?
            2. **By Product Line**: Which products drive our profits, and which ones are being sold at a loss?
            3. **By Customer Type**: Are corporate buyers or individual consumers more profitable, or do they perform about the same?
            """
        )

    render_data_dictionary_expander()

    if df.empty:
        st.warning("No records match the current parameter selection.")
        return

    # Direct Diagnostic Answers
    with st.container(border=True):
        st.markdown("### Key Findings on Countries, Products, and Customers")
        st.markdown(
            """
            * **Which countries and regions lose the most money?**
              - The **Middle East & Africa (EMEA)** region has the lowest profit margin among major markets at **5.45%** (\\$43.9K profit on \\$806K sales).
              - **The 4 Biggest Money-Losing Countries**:
                1. **Turkey**: **-\\$98,447 net loss** on \\$108.5K sales (**-90.7% margin**, average discount: 60.0%).
                2. **Nigeria**: **-\\$80,751 net loss** on \\$54.4K sales (**-148.6% margin**, average discount: 70.0%).
                3. **Netherlands**: **-\\$41,070 net loss** on \\$77.5K sales (**-53.0% margin**, average discount: 48.2%).
                4. **Honduras**: **-\\$29,482 net loss** on \\$90.1K sales (**-32.7% margin**, average discount: 40.7%).
            * **Which product lines are losing money?**
              - **Tables** is the **only product category that loses money**, generating **-\\$64,083 in cumulative losses** on \\$757,042 in sales (-8.5% margin).
              - **Customers want tables, but we price them poorly**: Tables had strong sales (\\$757K revenue, 3,083 units). But giving **29.1% average promotional discounts** on large, heavy furniture meant that shipping costs wiped out all the profit on every order.
            * **How concentrated are these losses?**
              - The top 10 loss-making countries alone account for over **-\\$355,000 in lost profit**.
            """
        )

    st.divider()

    tab_quadrant, tab_geo, tab_prod, tab_segment, tab_loss_table = st.tabs(
        [
            "Country Performance Matrix (147 Countries)",
            "Geographic Drilldown (Markets & Countries)",
            "Product Lines & Categories",
            "Customer Types (Consumer vs Business)",
            "Audit Trail: Money-Losing Orders",
        ]
    )

    # 1. Feature: Country Performance Matrix
    with tab_quadrant:
        with st.container(border=True):
            st.markdown("### Country Performance Matrix (All 147 Countries)")
            st.markdown(
                "This chart plots all 147 countries by total sales volume and profit margin, "
                "making it easy to see which markets drive our business and which ones lose money."
            )

            quad_df = compute_territory_quadrant_matrix(df)
            quad_chart = create_territory_quadrant_chart(quad_df)
            st.plotly_chart(quad_chart, width="stretch")

            render_chart_story_card(
                title="Performance Profiles of 147 International Markets",
                what_it_shows=(
                    "A 2x2 scatter matrix plotting countries by Total Sales ($ USD, log scale on X-axis) "
                    "and Profit Margin (%, Y-axis). Bubble size shows total number of orders. "
                    "The red line shows break-even (0% margin); the dotted green line shows our 10% target margin."
                ),
                key_takeaway=(
                    "Our 147 countries naturally fall into four clear groups: "
                    "1. Growth Engines (Green): High sales and high margins (US, UK, Germany, Australia, China, India). "
                    "2. Big Sales, Thin Margins (Amber): Large sales volume, but weak margins due to discounting (France, Philippines, Mexico). "
                    "3. High-Profit Gems (Blue): Moderate sales volume with excellent profit margins >15% (Canada, New Zealand, Norway). "
                    "4. Chronic Loss Makers (Red): Countries operating below zero profit (Turkey, Nigeria, Netherlands, Honduras)."
                ),
                business_impact=(
                    "We shouldn't treat all countries the same. We should invest heavily in our Growth Engines and Gems, "
                    "tighten pricing in Thin Margin markets, and stop direct shipping subsidies in Chronic Loss markets."
                ),
                recommendation=(
                    "Give local sales teams pricing flexibility only in proven profitable countries. "
                    "In loss-making countries, strictly cap discounts at checkout."
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
                width="stretch",
            )

    # 2. Geographic Drilldown
    with tab_geo:
        mkt_df, reg_df, country_df = analyze_geographic_drilldown(df)

        c1, c2 = st.columns([3, 2])
        with c1:
            with st.container(border=True):
                st.markdown("#### The 10 Biggest Money-Losing Countries")
                loss_chart = create_country_loss_chart(country_df, bottom_n=10)
                st.plotly_chart(loss_chart, width="stretch")

                render_chart_story_card(
                    title="Countries with the Largest Operating Losses",
                    what_it_shows=(
                        "A ranking of the 10 countries with the largest total losses. "
                        "Red bars indicate the exact dollar amount lost in each country."
                    ),
                    key_takeaway=(
                        "Losses are heavily concentrated: Turkey (-$98.4K on $108.5K sales) and Nigeria (-$80.8K on $54.4K sales) "
                        "have staggering loss margins (-90.7% and -148.6%). Together, these two countries alone burned $179K, "
                        "caused by huge baseline discounts of 60% to 70%."
                    ),
                    business_impact=(
                        "Our standard pricing and shipping policies don't work in high-cost or high-tariff countries. "
                        "Local sales reps gave away massive discounts to hit volume quotas, while the company absorbed "
                        "expensive international air shipping and customs fees."
                    ),
                    recommendation=(
                        "Immediately stop giving large discounts in Turkey, Nigeria, and the Netherlands. "
                        "Switch from direct international shipping to partnering with local distributors who manage their own domestic delivery."
                    ),
                )

        with c2:
            with st.container(border=True):
                st.markdown("#### Sales Share by Global Market")
                pie_chart = create_market_share_pie(mkt_df)
                st.plotly_chart(pie_chart, width="stretch")

                render_chart_story_card(
                    title="Sales Distribution Across Global Regions",
                    what_it_shows="The share of total company sales coming from each of the seven global markets.",
                    key_takeaway=(
                        "APAC ($3.59M, 28.4%), EU ($2.94M, 23.2%), and the US ($2.30M, 18.2%) make up nearly 70% of all sales, "
                        "all with solid profit margins around 12.2% to 12.7%. Meanwhile, EMEA ($806K, 6.4%) generates a weak 5.45% margin."
                    ),
                    business_impact="Our biggest core markets are financially healthy; losses in EMEA and Africa pull down overall company performance.",
                    recommendation="Keep margins strong in our primary markets while fixing fulfillment and pricing across EMEA and Africa.",
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
                st.plotly_chart(reg_fig, width="stretch")
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
                    width="stretch",
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
                width="stretch",
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
                width="stretch",
            )

    # 3. Product Drilldown
    with tab_prod:
        cat_df, subcat_df = analyze_product_breakdown(df)

        with st.container(border=True):
            st.markdown("#### Merchandise Line Profitability Distribution")
            subcat_chart = create_subcat_profit_chart(subcat_df)
            st.plotly_chart(subcat_chart, width="stretch")

            render_chart_story_card(
                title="Product Line Profitability: Tables Is the Only Loss-Maker",
                what_it_shows=(
                    "A horizontal bar chart comparing profits across all 17 product categories. "
                    "Green bars show profitable categories; the red bar highlights Tables as the only money-losing line."
                ),
                key_takeaway=(
                    "Tech products (Copiers +$258.6K, Phones +$216.7K, Accessories +$129.6K) and Office Supplies (Storage +$108.5K, Binders +$72.4K) "
                    "bring in great profits. Tables is the only category that lost money (-$64,083 loss) despite bringing in $757K in sales."
                ),
                business_impact=(
                    "Tables suffers from bad pricing on bulky freight. Heavy boxes cost a lot to ship. "
                    "Giving an average 29.1% discount on bulky items guarantees that every single table shipped loses money."
                ),
                recommendation=(
                    "Overhaul the Tables catalog: add standard oversized shipping fees, raise base catalog prices, and cap discounts at 10%."
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
                    width="stretch",
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
                    width="stretch",
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
            st.plotly_chart(segment_chart, width="stretch")

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
                width="stretch",
            )

            render_chart_story_card(
                title="Customer Types Perform Almost Identically",
                what_it_shows="Financial performance across Consumer, Corporate, and Home Office buyers.",
                key_takeaway=(
                    "All three customer types deliver virtually identical profit margins: Consumer (11.51%), Corporate (11.54%), "
                    "and Home Office (11.99%), with average discounts sitting right around 14%."
                ),
                business_impact=(
                    "This proves that our profit problem is not caused by who we sell to. All customer types are equally profitable under normal pricing. "
                    "The problem is purely about where we sell (specific countries) and how we discount (discounts over 20%)."
                ),
                recommendation="Keep our current sales teams and customer segments as they are; focus fixes entirely on discount caps and shipping costs.",
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
                width="stretch",
            )

            csv_loss = loss_df[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Negative-Margin Audit Records (CSV)",
                data=csv_loss,
                file_name="global_superstore_negative_margin_transactions.csv",
                mime="text/csv",
            )

    st.divider()

    # Chapter 2 - what this evidence changes
    with st.container(border=True):
        st.markdown("### Chapter 2 Actions: Stop the Named Leaks")
        st.markdown(
            r"""
            Based on the geographic and product analysis, we recommend three specific actions:

            1. **Fix the Four High-Loss Countries (Turkey, Nigeria, Netherlands, Honduras)**:
               - *Action*: Stop shipping orders directly from international warehouses into Turkey (-\$98.4K loss) and Nigeria (-\$80.8K loss). Partner with local in-country distributors and warehouses that handle domestic shipping with prices set in local currencies.
               - *Profit Recovered*: **Saves +\$179,198 in direct bilateral deficits** across Turkey and Nigeria (and up to +\$249,750 across all four high-loss countries).

            2. **Fix the Tables Category (Add Shipping Fees & Limit Discounts)**:
               - *Action*: Customers want tables, but our pricing loses money. Update the table catalog: add standard oversized shipping fees on bulky deliveries, stop offering free express shipping, and drop models that lose money.
               - *Profit Recovered*: **+\$46,245 in recovered shipping fees and over +\$80,000 in total margin turnaround**, turning Tables into a profitable category.

            3. **Keep Customer Segments As They Are**:
               - *Action*: Keep our current customer sales structure (Consumer, Corporate, Home Office). The data shows all three groups perform equally well (~11.5% margin), so changing them won't solve the problem.
            """
        )
