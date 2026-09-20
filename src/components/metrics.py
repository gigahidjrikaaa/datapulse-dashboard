"""Institutional executive KPI metric card components for Global Superstore."""

import streamlit as st


def render_kpi_cards(kpi_data: dict[str, float]) -> None:
    """Render a responsive grid of executive KPI metric cards with formal corporate styling.

    Args:
        kpi_data: Dictionary produced by analyzer.compute_overview_kpis.
    """
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            label="Gross Invoiced Revenue",
            value=f"${kpi_data.get('total_sales', 0.0):,.0f}",
            delta="2011–2014 Cumulative",
            delta_color="normal",
        )

    with c2:
        st.metric(
            label="Net Operating Profit",
            value=f"${kpi_data.get('total_profit', 0.0):,.0f}",
            delta=f"{kpi_data.get('profit_margin', 0.0):.1f}% Margin",
            delta_color="normal",
        )

    with c3:
        loss_drag = kpi_data.get("profit_loss_drag", 0.0)
        st.metric(
            label="Negative Margin Drag",
            value=f"-${loss_drag:,.0f}",
            delta=f"{kpi_data.get('loss_order_pct', 0.0):.1f}% of order lines",
            delta_color="inverse",
        )

    with c4:
        gain = kpi_data.get("profitable_order_gain", 0.0)
        st.metric(
            label="Gross Profitable Contribution",
            value=f"${gain:,.0f}",
            delta="Base earnings power",
            delta_color="normal",
        )

    with c5:
        net = kpi_data.get("total_profit", 1.0)
        upside_pct = (loss_drag / net * 100.0) if net > 0 else 0.0
        st.metric(
            label="EBITDA Recovery Potential",
            value=f"+{upside_pct:.1f}%",
            delta="Via pricing governance",
            delta_color="normal",
        )


def render_kpi_card(
    title: str,
    value: str,
    sub_value: str = "",
    delta_color: str = "normal",
) -> None:
    """Render a single institutional KPI metric card.

    Args:
        title: Metric label.
        value: Formatted primary metric value.
        sub_value: Formatted secondary descriptive text or delta.
        delta_color: Metric delta indicator color mode ('normal', 'inverse', 'off').
    """
    st.metric(
        label=title,
        value=value,
        delta=sub_value if sub_value else None,
        delta_color=delta_color,
    )
