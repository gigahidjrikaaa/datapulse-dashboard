"""Plotly exhibits for the predictive analytics layer (Section 5)."""

import pandas as pd
import plotly.graph_objects as go

from src.config import ACCENT_CYAN, CHART_TEMPLATE, DANGER_COLOR, PRIMARY_COLOR, SUCCESS_COLOR


def create_sales_forecast_chart(fc: dict) -> go.Figure:
    """History (actuals), the forward forecast, and its 80% prediction interval."""
    history: pd.DataFrame = fc["history"]
    forecast: pd.DataFrame = fc["forecast"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=history["date"],
            y=history["actual"],
            name="Actual sales (FY2011-FY2014)",
            mode="lines",
            line=dict(color=PRIMARY_COLOR, width=2.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["date"],
            y=forecast["lower_80"],
            name="80% interval",
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["date"],
            y=forecast["upper_80"],
            name="80% prediction interval",
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(8, 145, 178, 0.18)",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["date"],
            y=forecast["forecast"],
            name=f"Forecast: {fc['model_used']}",
            mode="lines+markers",
            line=dict(color=ACCENT_CYAN, width=2.5, dash="dash"),
            marker=dict(size=6),
        )
    )
    divider = str(history["date"].iloc[-1].date())
    fig.add_shape(type="line", x0=divider, x1=divider, y0=0, y1=1, yref="paper", line=dict(color="#94A3B8", dash="dot"))
    fig.add_annotation(
        x=divider, y=1, yref="paper", text="Forecast starts", showarrow=False, yanchor="bottom", font=dict(color="#94A3B8")
    )
    fig.update_layout(
        template=CHART_TEMPLATE,
        title="Monthly Sales: Actuals and 12-Month Forecast (FY2015)",
        xaxis_title="Month",
        yaxis_title="Sales ($ USD)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_discount_response_chart(dr: dict) -> go.Figure:
    """Predicted volume index by discount depth (0% discount = 100), with the 20% cap marked."""
    curve = pd.DataFrame(dr["curve"])
    idx_at = lambda d: float(curve.loc[curve["discount"] == d, "volume_index"].iloc[0])  # noqa: E731

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=curve["discount"] * 100.0,
            y=curve["volume_index"],
            name="Predicted volume (index, 0% = 100)",
            mode="lines+markers+text",
            text=[f"{v:.0f}" for v in curve["volume_index"]],
            textposition="top center",
            line=dict(color=ACCENT_CYAN, width=2.5),
            marker=dict(size=8),
        )
    )
    fig.add_hline(y=100.0, line_dash="dot", line_color="#94A3B8", annotation_text="No-discount baseline (100)")
    fig.add_vline(x=20.0, line_dash="dash", line_color=DANGER_COLOR, annotation_text="20% cap")
    fig.update_layout(
        template=CHART_TEMPLATE,
        title=(
            "Predicted Demand Response to Discount Depth: "
            f"capping at 20% retains {next(r['retained_pct'] for r in dr['retention'] if r['cap'] == 0.20):.0f}% of volume"
        ),
        xaxis_title="Discount rate (%)",
        yaxis_title="Predicted volume index (0% discount = 100)",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_churn_lift_chart(cr: dict, n_deciles: int = 10) -> go.Figure:
    """Actual lapse rate per model-scored decile - a lift chart validating the churn model."""
    scores: pd.DataFrame = cr["customer_scores"].copy()
    scores["decile"] = pd.qcut(scores["p_lapse"].rank(method="first"), n_deciles, labels=range(1, n_deciles + 1))
    by_decile = scores.groupby("decile", observed=True)["lapsed"].agg(["mean", "size"]).reset_index()
    overall = cr["lapse_rate_pct"] / 100.0

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[f"D{int(d)}" for d in by_decile["decile"]],
            y=by_decile["mean"] * 100.0,
            name="Actual lapse rate by risk decile (D10 = highest risk)",
            marker_color=[DANGER_COLOR if i >= n_deciles - 2 else PRIMARY_COLOR for i in range(n_deciles)],
            text=[f"{v * 100.0:.0f}%" for v in by_decile["mean"]],
            textposition="outside",
        )
    )
    fig.add_hline(
        y=overall * 100.0,
        line_dash="dash",
        line_color="#E2E8F0",
        annotation_text=f"Average lapse rate ({overall * 100.0:.1f}%)",
    )
    fig.update_layout(
        template=CHART_TEMPLATE,
        title=f"Churn Model Lift: Actual Lapse Rate per Risk Decile (AUC {cr['auc_test']:.2f})",
        xaxis_title="Model risk decile (D1 = lowest predicted risk, D10 = highest)",
        yaxis_title="Actual lapse rate (%)",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_policy_profit_surface_chart(grid: pd.DataFrame, best: dict) -> go.Figure:
    """Heatmap of projected operating profit across the discount-cap x surcharge policy grid.

    The profit-maximizing cell is marked; the row at the recommended 20% cap is outlined so
    the board can see how close the rest of the surface sits to the recommended 20% plan.

    Args:
        grid: Ranked policy grid from optimize_turnaround_policy.
        best: The grid's best-policy row.

    Returns:
        Plotly Figure.
    """
    caps = sorted(grid["cap_value"].unique())
    surcharges = sorted(grid["surcharge_value"].unique())
    z = []
    for cap in caps:
        row = []
        for sur in surcharges:
            match = grid[
                (grid["cap_value"] == cap) & (grid["surcharge_value"] == sur)
            ]["Projected operating profit"]
            row.append(float(match.iloc[0]) / 1e6 if len(match) else float("nan"))
        z.append(row)

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=[f"${s:.0f}" for s in surcharges],
            y=[f"{c * 100:.0f}%" for c in caps],
            text=[[f"${v:.2f}M" for v in row] for row in z],
            texttemplate="%{text}",
            colorscale="Tealrose",
            reversescale=True,
            colorbar=dict(title="Projected<br>profit ($M)"),
        )
    )
    fig.update_layout(
        template=CHART_TEMPLATE,
        title=(
            f"Policy Profit Surface (measured demand): optimum at {best['Discount cap']} cap, "
            f"{best['Tables surcharge']} surcharge"
        ),
        xaxis_title="Tables oversized-freight surcharge",
        yaxis_title="Discount cap",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig
