"""Prescriptive layer: policy simulation with the MEASURED demand response and a
grid-search optimizer over discount caps and Tables surcharges.

Where `analyzer.simulate_turnaround_impact` treats churn as an assumed input (and scales
it by an arbitrary 0.25 drag factor), this module prices the volume effect of a discount
cap from the Section 5 response model: every affected line is re-priced at the cap and its
quantity scaled by the model-implied retention ratio. No assumed churn, no fudge factor.
"""

from typing import Any

import numpy as np
import pandas as pd

from src.services.predictive import analyze_discount_response

DEFAULT_CAPS = [0.10, 0.15, 0.20, 0.25, 0.30]
DEFAULT_SURCHARGES = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0]


def measure_retention_by_cap(df: pd.DataFrame, caps: list[float]) -> dict[float, float]:
    """Measured volume-retention ratio (0-1+) per discount cap, from the response model."""
    unique = sorted(set(round(float(c), 4) for c in caps))
    result = analyze_discount_response(df, caps=unique)
    return {round(float(r["cap"]), 4): float(r["retained_pct"]) / 100.0 for r in result["retention"]}


def simulate_turnaround_measured(
    df: pd.DataFrame,
    discount_cap: float,
    table_freight_surcharge: float = 15.0,
    restructure_deficit_territories: bool = True,
    retention_ratio: float | None = None,
) -> dict[str, Any]:
    """Simulate the turnaround with the cap's volume effect taken from the response model.

    Same lever semantics as `analyzer.simulate_turnaround_impact`, except the volume drag
    is measured rather than assumed: each affected line is re-priced to the cap and its
    quantity scaled by the model-implied retention ratio (cost scales with units, the
    price uplift survives only on the units retained).

    Args:
        df: Order-line DataFrame (full ledger for company-level policy, or a segment slice).
        discount_cap: Maximum discount allowed (e.g. 0.20).
        table_freight_surcharge: Dollars per Tables unit passed through to customers.
        restructure_deficit_territories: Apply the Turkey & Nigeria 3PL recovery.
        retention_ratio: Pre-measured volume retention at this cap (0-1+). Computed from
            the response model when omitted.

    Returns:
        Same key set as `simulate_turnaround_impact` plus 'volume_ratio'.
    """
    if df.empty:
        return {"error": "Empty dataframe."}

    if retention_ratio is None:
        retention_ratio = measure_retention_by_cap(df, [discount_cap]).get(round(float(discount_cap), 4), 1.0)

    baseline_sales = float(df["Sales"].sum())
    baseline_profit = float(df["Profit"].sum())
    baseline_margin = baseline_profit / baseline_sales * 100.0 if baseline_sales > 0 else 0.0

    capped = df[df["Discount"] > discount_cap]
    if capped.empty:
        pricing_recovery = 0.0
        sales_delta = 0.0
        affected = 0
    else:
        safe = (1.0 - capped["Discount"]).replace(0, 0.001)
        list_price = capped["Sales"] / safe
        new_sales_full = float((list_price * (1.0 - discount_cap)).sum())
        cost = float((capped["Sales"] - capped["Profit"]).sum())
        # Volume response scales both revenue and cost; the price uplift survives on retained units
        new_sales = new_sales_full * retention_ratio
        new_cost = cost * retention_ratio
        pricing_recovery = new_sales - new_cost - float(capped["Profit"].sum())
        sales_delta = new_sales - float(capped["Sales"].sum())
        affected = int(len(capped))

    if restructure_deficit_territories and "Country" in df.columns:
        deficit = df[df["Country"].isin(["Turkey", "Nigeria"])]["Profit"].sum()
        territory_recovery = abs(float(deficit)) if deficit < 0 else 0.0
    else:
        territory_recovery = 0.0

    if table_freight_surcharge > 0 and "Sub-Category" in df.columns:
        tables_units = float(df.loc[df["Sub-Category"] == "Tables", "Quantity"].sum())
        tables_recovery = tables_units * table_freight_surcharge
    else:
        tables_recovery = 0.0

    projected_profit = baseline_profit + pricing_recovery + territory_recovery + tables_recovery
    projected_sales = baseline_sales + sales_delta
    projected_margin = projected_profit / projected_sales * 100.0 if projected_sales > 0 else 0.0
    uplift = projected_profit - baseline_profit

    return {
        "discount_cap": float(discount_cap),
        "table_freight_surcharge": float(table_freight_surcharge),
        "restructure_deficit_territories": bool(restructure_deficit_territories),
        "volume_ratio": float(retention_ratio),
        "baseline_sales": baseline_sales,
        "baseline_profit": baseline_profit,
        "baseline_margin": baseline_margin,
        "pricing_recovery": float(pricing_recovery),
        "territory_recovery": territory_recovery,
        "table_freight_recovery": tables_recovery,
        "attrition_drag": 0.0,  # measured, not assumed - already inside pricing_recovery
        "affected_orders_count": affected,
        "projected_sales": projected_sales,
        "projected_profit": float(projected_profit),
        "projected_margin": float(projected_margin),
        "net_ebitda_uplift": float(uplift),
    }


def optimize_turnaround_policy(
    df: pd.DataFrame,
    caps: list[float] | None = None,
    surcharges: list[float] | None = None,
    restructure_deficit_territories: bool = True,
) -> dict[str, Any]:
    """Grid-search the policy space (discount cap x Tables surcharge) with the measured
    demand response and rank every combination by projected operating profit.

    Args:
        df: Full order-line DataFrame.
        caps: Discount caps to search. Defaults to 10%-30% (the simulator's policy range).
        surcharges: Tables surcharges to search. Defaults to $0-$25.
        restructure_deficit_territories: Whether the 3PL lever is on for every cell.

    Returns:
        Dictionary with the ranked grid, the best policy, the baseline row, and the
        measured retention per cap.
    """
    caps = DEFAULT_CAPS if caps is None else list(caps)
    surcharges = DEFAULT_SURCHARGES if surcharges is None else list(surcharges)

    retention = measure_retention_by_cap(df, caps)

    baseline_profit = float(df["Profit"].sum())
    baseline_sales = float(df["Sales"].sum())

    rows = []
    for cap in caps:
        r = retention.get(round(float(cap), 4), 1.0)
        for surcharge in surcharges:
            res = simulate_turnaround_measured(
                df,
                discount_cap=cap,
                table_freight_surcharge=surcharge,
                restructure_deficit_territories=restructure_deficit_territories,
                retention_ratio=r,
            )
            rows.append(
                {
                    "Discount cap": f"{cap * 100.0:.0f}%",
                    "cap_value": float(cap),
                    "Tables surcharge": f"${surcharge:.0f}",
                    "surcharge_value": float(surcharge),
                    "Measured volume retention": f"{r * 100.0:.1f}%",
                    "Projected operating profit": res["projected_profit"],
                    "Projected margin": res["projected_margin"],
                    "Net profit uplift": res["net_ebitda_uplift"],
                    "Uplift %": res["net_ebitda_uplift"] / baseline_profit * 100.0 if baseline_profit > 0 else 0.0,
                }
            )
    grid = pd.DataFrame(rows).sort_values("Projected operating profit", ascending=False, ignore_index=True)
    best = grid.iloc[0].to_dict()

    return {
        "grid": grid,
        "best": best,
        "baseline_profit": baseline_profit,
        "baseline_sales": baseline_sales,
        "retention_by_cap": retention,
        "n_policies": int(len(grid)),
    }


def best_cap_by_market(
    df: pd.DataFrame,
    caps: list[float] | None = None,
    table_freight_surcharge: float = 15.0,
) -> pd.DataFrame:
    """Best discount cap per global market, holding the other levers at the base case.

    Uses the global response model's retention for each cap (a per-market response model
    would need more data per cell than this ledger supports).

    Args:
        df: Full order-line DataFrame.
        caps: Discount caps to evaluate. Defaults to the standard policy grid.
        table_freight_surcharge: Tables surcharge held constant across markets.

    Returns:
        DataFrame with each market's best cap, the profit at that cap, and the profit
        at the recommended global 20% cap for comparison.
    """
    caps = DEFAULT_CAPS if caps is None else list(caps)
    rows = []
    for market, mdf in df.groupby("Market"):
        retention = measure_retention_by_cap(mdf, caps)
        profits = {}
        for cap in caps:
            res = simulate_turnaround_measured(
                mdf,
                discount_cap=cap,
                table_freight_surcharge=table_freight_surcharge,
                restructure_deficit_territories=True,
                retention_ratio=retention.get(round(float(cap), 4), 1.0),
            )
            profits[cap] = res["projected_profit"]
        best_cap = max(profits, key=profits.get)
        rows.append(
            {
                "Market": market,
                "Ledger profit": float(mdf["Profit"].sum()),
                "Best cap": f"{best_cap * 100.0:.0f}%",
                "Profit at best cap": profits[best_cap],
                "Profit at global 20% cap": profits.get(0.20, float("nan")),
            }
        )
    out = pd.DataFrame(rows)
    out["Uplift from tuning (vs global 20%)"] = out["Profit at best cap"] - out["Profit at global 20% cap"]
    return out.sort_values("Ledger profit", ascending=False, ignore_index=True)
