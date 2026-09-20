"""Interactive visualization components built with Plotly for Global Superstore."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import (
    CHART_COLORWAY,
    CHART_TEMPLATE,
    DANGER_COLOR,
    PRIMARY_COLOR,
    SUCCESS_COLOR,
    WARNING_COLOR,
)


def create_yoy_growth_chart(yearly_df: pd.DataFrame) -> go.Figure:
    """Create a dual-axis chart showing YoY Sales and Profit progression with Margin %.

    Args:
        yearly_df: Yearly aggregated DataFrame.

    Returns:
        Plotly Figure.
    """
    if yearly_df.empty:
        return go.Figure()

    fig = go.Figure()

    # Sales Bar
    fig.add_trace(
        go.Bar(
            x=yearly_df["Year"].astype(str),
            y=yearly_df["Sales"],
            name="Gross Sales ($ USD)",
            marker_color=PRIMARY_COLOR,
            opacity=0.85,
        )
    )

    # Profit Bar
    fig.add_trace(
        go.Bar(
            x=yearly_df["Year"].astype(str),
            y=yearly_df["Profit"],
            name="Operating Profit ($ USD)",
            marker_color=SUCCESS_COLOR,
        )
    )

    # Margin Line (Secondary Y-Axis)
    fig.add_trace(
        go.Scatter(
            x=yearly_df["Year"].astype(str),
            y=yearly_df["Profit_Margin"],
            name="Operating Margin (%)",
            yaxis="y2",
            mode="lines+markers+text",
            text=[f"{m:.1f}%" for m in yearly_df["Profit_Margin"]],
            textposition="top center",
            line=dict(color=WARNING_COLOR, width=2.5),
            marker=dict(size=8, color=WARNING_COLOR),
        )
    )

    fig.update_layout(
        template=CHART_TEMPLATE,
        title="Annual Revenue, Operating Profit, and Margin Progression (2011–2014)",
        barmode="group",
        xaxis_title="Fiscal Year",
        yaxis=dict(title="Financial Value (USD)"),
        yaxis2=dict(
            title="Operating Margin (%)",
            overlaying="y",
            side="right",
            showgrid=False,
            range=[0, 25],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=50, t=60, b=40),
    )
    return fig


def create_monthly_trend_chart(monthly_df: pd.DataFrame) -> go.Figure:
    """Create continuous monthly timeline chart.

    Args:
        monthly_df: Monthly aggregated DataFrame.

    Returns:
        Plotly Figure.
    """
    if monthly_df.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly_df["Period"],
            y=monthly_df["Sales"],
            name="Monthly Invoiced Sales ($)",
            mode="lines",
            line=dict(color=PRIMARY_COLOR, width=2),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.12)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_df["Period"],
            y=monthly_df["Profit"],
            name="Monthly Net Operating Profit ($)",
            mode="lines+markers",
            line=dict(color=SUCCESS_COLOR, width=2),
        )
    )

    fig.update_layout(
        template=CHART_TEMPLATE,
        title="Monthly Revenue and Net Profit Trajectory (48-Month Operational Horizon)",
        xaxis_title="Reporting Period",
        yaxis_title="Financial Value (USD)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_discount_cliff_chart(disc_df: pd.DataFrame) -> go.Figure:
    """Create bar chart demonstrating unit economics across discount tiers.

    Args:
        disc_df: DataFrame aggregated by Discount_Bucket.

    Returns:
        Plotly Figure.
    """
    if disc_df.empty:
        return go.Figure()

    colors = [
        SUCCESS_COLOR if row["Profit_Margin"] > 0 else DANGER_COLOR
        for _, row in disc_df.iterrows()
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=disc_df["Discount_Bucket"].astype(str),
            y=disc_df["Profit_Margin"],
            marker_color=colors,
            text=[f"{m:.1f}%" for m in disc_df["Profit_Margin"]],
            textposition="auto",
            name="Operating Margin (%)",
        )
    )

    # Reference break-even threshold line
    fig.add_hline(y=0, line_dash="dash", line_color="#94A3B8", annotation_text="Break-Even Threshold (0.0% Margin)")

    fig.update_layout(
        template=CHART_TEMPLATE,
        title="Operating Margin by Discount Bracket: Unit Economics Inversion Threshold",
        xaxis_title="Contractual Discount Bracket",
        yaxis_title="Operating Profit Margin (%)",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_country_loss_chart(country_df: pd.DataFrame, bottom_n: int = 10) -> go.Figure:
    """Create a horizontal bar chart showing territories with largest operating deficits.

    Args:
        country_df: Country aggregated DataFrame.
        bottom_n: Number of bottom countries to display.

    Returns:
        Plotly Figure.
    """
    if country_df.empty:
        return go.Figure()

    bottom_countries = (
        country_df[country_df["Profit"] < 0]
        .sort_values(by="Profit", ascending=True)
        .head(bottom_n)
    )

    if bottom_countries.empty:
        return go.Figure()

    fig = px.bar(
        bottom_countries,
        x="Profit",
        y="Country",
        orientation="h",
        title=f"Territories with Largest Operating Deficits (Cumulative Negative Profit, Top {len(bottom_countries)})",
        labels={"Profit": "Cumulative Operating Deficit ($ USD)", "Country": "Sovereign Territory"},
        color_discrete_sequence=[DANGER_COLOR],
        template=CHART_TEMPLATE,
        text=bottom_countries["Profit"].apply(lambda x: f"-${abs(x):,.0f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(l=40, r=60, t=60, b=40),
    )
    return fig


def create_subcat_profit_chart(subcat_df: pd.DataFrame) -> go.Figure:
    """Create a diverging bar chart showing Sub-Category Profitability.

    Args:
        subcat_df: Sub-Category aggregated DataFrame.

    Returns:
        Plotly Figure.
    """
    if subcat_df.empty:
        return go.Figure()

    sorted_df = subcat_df.sort_values(by="Profit", ascending=True)
    colors = [
        SUCCESS_COLOR if p > 0 else DANGER_COLOR for p in sorted_df["Profit"]
    ]

    fig = go.Figure(
        go.Bar(
            x=sorted_df["Profit"],
            y=sorted_df["Sub-Category"],
            orientation="h",
            marker_color=colors,
            text=[f"${p:,.0f}" for p in sorted_df["Profit"]],
            textposition="auto",
        )
    )

    fig.update_layout(
        template=CHART_TEMPLATE,
        title="Net Operating Profit by Merchandise Sub-Category (17 Portfolio Segments)",
        xaxis_title="Net Operating Profit ($ USD)",
        yaxis_title="Merchandise Line",
        margin=dict(l=40, r=50, t=60, b=40),
    )
    return fig


def create_market_share_pie(market_df: pd.DataFrame) -> go.Figure:
    """Create a donut chart illustrating Market Sales Contribution.

    Args:
        market_df: Market aggregated DataFrame.

    Returns:
        Plotly Figure.
    """
    if market_df.empty:
        return go.Figure()

    fig = px.pie(
        market_df,
        names="Market",
        values="Sales",
        hole=0.45,
        title="Regional Market Sales Distribution",
        color_discrete_sequence=CHART_COLORWAY,
        template=CHART_TEMPLATE,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig


def create_territory_quadrant_chart(quadrant_df: pd.DataFrame) -> go.Figure:
    """Create a 2x2 Strategic Portfolio Bubble Matrix for 147 operating territories.

    Args:
        quadrant_df: Territory aggregated DataFrame from compute_territory_quadrant_matrix.

    Returns:
        Plotly Figure.
    """
    if quadrant_df.empty:
        return go.Figure()

    color_map = {
        "Core Value Engine": "#059669",               # Green
        "Margin-Diluted Volume Channel": "#D97706",    # Amber
        "High-Yield Niche Profit Center": "#2563EB",   # Blue
        "Deficit Rationalization Priority": "#DC2626", # Red
        "Secondary Developing Territory": "#64748B",   # Slate Grey
    }

    fig = px.scatter(
        quadrant_df,
        x="Sales",
        y="Profit_Margin",
        size="Orders",
        size_max=35,
        color="Portfolio_Quadrant",
        color_discrete_map=color_map,
        hover_name="Country",
        hover_data={
            "Market": True,
            "Sales": ":$,.0f",
            "Profit": ":$,.0f",
            "Profit_Margin": ":.1f%",
            "Avg_Discount_Pct": ":.1f%",
            "Orders": ":,",
            "Portfolio_Quadrant": True,
        },
        title="Strategic Portfolio Matrix: 147 Sovereign Operating Territories",
        labels={
            "Sales": "Gross Sales Volume ($ USD, Log Scale)",
            "Profit_Margin": "Operating Profit Margin (%)",
            "Portfolio_Quadrant": "Strategic Portfolio Classification",
        },
        template=CHART_TEMPLATE,
        log_x=True,
    )

    # Reference lines for break-even margin (0.0%) and healthy benchmark (10.0%)
    fig.add_hline(y=0.0, line_dash="dash", line_color="#DC2626", annotation_text="Break-Even (0.0% Margin)")
    fig.add_hline(y=10.0, line_dash="dot", line_color="#059669", annotation_text="Target Benchmark (10.0% Margin)")

    fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#334155")))
    fig.update_layout(
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def create_ebitda_bridge_chart(bridge_components: dict[str, float]) -> go.Figure:
    """Create a Plotly Waterfall chart illustrating the EBITDA Turnaround Bridge.

    Args:
        bridge_components: Dictionary of waterfall labels and dollar values.

    Returns:
        Plotly Figure.
    """
    if not bridge_components:
        return go.Figure()

    labels = list(bridge_components.keys())
    values = list(bridge_components.values())

    # Build measures: 'relative' for adjustments, 'total' for projected final
    measures = ["absolute" if i == 0 else "total" if i == len(labels) - 1 else "relative" for i in range(len(labels))]

    fig = go.Figure(
        go.Waterfall(
            name="EBITDA Bridge",
            orientation="v",
            measure=measures,
            x=labels,
            textposition="outside",
            text=[f"${abs(v):,.0f}" if v >= 0 else f"-${abs(v):,.0f}" for v in values],
            y=values,
            connector={"line": {"color": "#64748B"}},
            decreasing={"marker": {"color": DANGER_COLOR}},
            increasing={"marker": {"color": SUCCESS_COLOR}},
            totals={"marker": {"color": PRIMARY_COLOR}},
        )
    )

    fig.update_layout(
        template=CHART_TEMPLATE,
        title="Executive EBITDA Recovery Bridge: Baseline to Projected Operating Profit",
        xaxis_title="Turnaround Strategic Driver",
        yaxis_title="Net Operating Profit ($ USD)",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig
