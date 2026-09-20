import re
from typing import Optional
import streamlit as st


def sanitize_markdown_text(text: str) -> str:
    """Escape currency dollar signs in markdown strings to prevent KaTeX math mode corruption.

    In Streamlit, multiple unescaped '$' symbols cause text to be rendered as LaTeX math formulas,
    stripping whitespace and italicizing characters. Escaping as r'\$' forces standard text rendering.

    Args:
        text: Input markdown text.

    Returns:
        Sanitized markdown text with escaped dollar signs.
    """
    if not text:
        return text
    # Escape any '$' that is not already preceded by a backslash
    return re.sub(r"(?<!\\)\$", r"\$", text)


def render_data_dictionary_expander() -> None:
    """Render a formal Data Dictionary & Financial Accounting Methodology expander."""
    with st.expander("Data Dictionary and Financial Accounting Methodology", expanded=False):
        st.markdown(
            """
            ### Transaction Ledger Dimensions (51,290 Records across 147 Countries)
            | Field Name | Domain | Data Type | Analytical Scope & Operational Relevance |
            | :--- | :--- | :--- | :--- |
            | **Order ID** | Order Governance | Alphanumeric | Unique transaction identifier. A single commercial purchase order may encompass multiple discrete item line items. |
            | **Order Date** | Temporal | Datetime | Date of purchase order entry (format: `DD-MM-YYYY`, range: 2011 through 2014). |
            | **Ship Date** | Logistics | Datetime | Date of physical dispatch from the regional fulfillment distribution center. |
            | **Ship Mode** | Fulfillment | Categorical | Logistics service level agreement: *Same Day*, *First Class*, *Second Class*, or *Standard Class*. |
            | **Customer ID / Name** | Commercial | Alphanumeric | Unique customer corporate account code and institutional entity name. |
            | **Segment** | Market Tier | Categorical | Client classification: *Consumer* (retail individual), *Corporate* (B2B middle market), or *Home Office* (SMB). |
            | **City / State / Country** | Territorial | Categorical | Destination market territory across 147 sovereign jurisdictions. |
            | **Market / Region** | Territorial | Categorical | Macro geographic operating theater: *APAC*, *EU*, *US*, *LATAM*, *EMEA*, *Africa*, *Canada*. |
            | **Product ID / Name** | Merchandise | Alphanumeric | Unique stock keeping unit (SKU) identifier and product catalog description. |
            | **Category** | Merchandise | Categorical | Primary merchandising division: *Technology*, *Furniture*, or *Office Supplies*. |
            | **Sub-Category** | Merchandise | Categorical | 17 distinct product sub-segments (e.g. *Phones*, *Chairs*, *Tables*, *Storage*, *Binders*). |
            | **Sales** | Financial | Numeric (USD) | Gross invoice value billed to client prior to post-sale allowances. |
            | **Quantity** | Volume | Integer | Units delivered per order line item. |
            | **Discount** | Commercial | Percentage | Contractual or promotional price concession applied at point-of-sale (range: 0.00 to 0.85). |
            | **Profit** | Financial | Numeric (USD) | Net operating profit after accounting for cost of goods sold (COGS) and freight delivery expense. |
            | **Shipping Cost** | Logistics | Numeric (USD) | Landed carrier freight expense incurred to deliver the order line. |
            | **Order Priority** | Operational | Categorical | Service level priority: *Critical*, *High*, *Medium*, or *Low*. |

            ---

            ### Financial Metrics and Valuation Formulas
            * **Operating Profit Margin (%)**:
              $$\\text{Operating Margin} = \\frac{\\text{Net Operating Profit}}{\\text{Gross Sales}} \\times 100\\%$$
              - Measures net commercial conversion per dollar of revenue. Target institutional benchmark: **12.0% to 15.0%**.
            * **Negative Margin Loss Drag (USD)**:
              $$\\text{Loss Drag} = \\sum |\\text{Profit}| \\quad \\forall \\; \\text{Transactions where Profit} < 0$$
              - Quantifies the gross capital dilution destroyed by the 24.5% of order lines executed below cost-to-serve.
            * **Gross Profitable Contribution (USD)**:
              $$\\text{Profitable Contribution} = \\sum \\text{Profit} \\quad \\forall \\; \\text{Transactions where Profit} \\ge 0$$
              - Reflects the unburdened earning power of the company's core profitable business (\\$2.39M).
            * **Shipping Cost Absorption Ratio (%)**:
              $$\\text{Shipping Absorption} = \\frac{\\text{Shipping Cost}}{\\text{Gross Sales}} \\times 100\\%$$
              - Evaluates freight intensity. Absorption ratios exceeding 15.0% without freight pass-through surcharges systematically impair unit contribution.
            * **Unit Economics Inversion Bound (The 20% Discount Threshold)**:
              - Transactions discounted **below 20.0%** yield positive operating margins (+9.9% to +25.3%). Transactions discounted **at or above 20.0%** generate structural operating deficits (-5.5% to -196.1%).
            """
        )


def render_chart_story_card(
    title: str,
    what_it_shows: str,
    key_takeaway: str,
    business_impact: str,
    recommendation: Optional[str] = None,
) -> None:
    """Render a formal management consulting interpretation card paired with a visualization.

    Args:
        title: Title of the analytical section.
        what_it_shows: Technical explanation of metrics and parameters.
        key_takeaway: Core empirical variance or pattern identified.
        business_impact: Commercial risk, cost exposure, or capital allocation implications.
        recommendation: Recommended executive intervention or policy decision.
    """
    clean_title = sanitize_markdown_text(title)
    clean_shows = sanitize_markdown_text(what_it_shows)
    clean_takeaway = sanitize_markdown_text(key_takeaway)
    clean_impact = sanitize_markdown_text(business_impact)

    with st.expander(f"Analytical Diagnostic: {clean_title}", expanded=False):
        st.markdown(
            f"""
            * **Metric Scope & Visual Architecture**:
              {clean_shows}
            * **Empirical Diagnostic Finding**:
              {clean_takeaway}
            * **Commercial Risk & Capital Efficiency Exposure**:
              {clean_impact}
            """
        )
        if recommendation:
            clean_rec = sanitize_markdown_text(recommendation)
            st.markdown(
                f"""
                * **Executive Decision & Governance Intervention**:
                  {clean_rec}
                """
            )
