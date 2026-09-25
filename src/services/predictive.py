"""Predictive analytics service: forecasting, discount response, and churn risk models.

All models are dependency-free (numpy/pandas), validated on held-out data, and return
plain dictionaries/DataFrames so views and tests can inspect every intermediate value.
"""

from typing import Any

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Model 1: Monthly sales forecast
#   Candidate A: seasonal naive with drift (same month last year x drift)
#   Candidate B: damped log-linear trend x multiplicative month seasonality
#   The candidate with the lower backtest MAPE on the trailing holdout wins.
# ---------------------------------------------------------------------------

def _fit_seasonal_trend(log_sales: np.ndarray, months: np.ndarray) -> tuple[np.ndarray, dict[int, float], float]:
    """Fit OLS log-trend plus additive (in logs) month-of-year indices."""
    t = np.arange(len(log_sales), dtype=float)
    X = np.column_stack([np.ones(len(t)), t])
    beta, *_ = np.linalg.lstsq(X, log_sales, rcond=None)
    fitted = X @ beta
    resid = log_sales - fitted
    index: dict[int, float] = {}
    for m in range(1, 13):
        mask = months == m
        index[m] = float((log_sales[mask] - fitted[mask]).mean()) if mask.any() else 0.0
    center = float(np.mean(list(index.values())))
    index = {m: v - center for m, v in index.items()}
    sigma = float(np.std(resid, ddof=2)) if len(resid) > 2 else 0.0
    return beta, index, sigma


def _damped_trend_forecast(
    monthly: pd.Series, holdout: int, horizon: int, phi: float = 0.95
) -> dict[str, Any]:
    """Damped log-linear trend with multiplicative seasonality, backtested on the holdout."""
    y = np.log(monthly.values)
    cal = np.array(monthly.index.month)
    n = len(monthly)
    beta_tr, idx_tr, _ = _fit_seasonal_trend(y[:-holdout], cal[:-holdout])

    preds = []
    for j in range(holdout):
        damping = sum(phi**k for k in range(1, j + 2))
        pos = (n - holdout - 1) + damping
        preds.append(np.exp(beta_tr[0] + beta_tr[1] * pos + idx_tr[cal[n - holdout + j]]))
    actual = monthly.values[-holdout:]
    mape = float(np.mean(np.abs((np.array(preds) - actual) / actual)) * 100.0)
    bias = float(np.mean((np.array(preds) - actual) / actual) * 100.0)

    beta_f, idx_f, sigma_f = _fit_seasonal_trend(y, cal)
    fc, lo, hi = [], [], []
    z80 = 1.2816
    for j in range(horizon):
        damping = sum(phi**k for k in range(1, j + 2))
        pos = (n - 1) + damping
        month_j = ((cal[-1] + j) % 12) + 1
        plog = beta_f[0] + beta_f[1] * pos + idx_f[month_j]
        fc.append(np.exp(plog))
        lo.append(np.exp(plog - z80 * sigma_f))
        hi.append(np.exp(plog + z80 * sigma_f))
    return {"forecast": np.array(fc), "lower": np.array(lo), "upper": np.array(hi), "mape": mape, "bias": bias}


def _seasonal_naive_drift_forecast(monthly: pd.Series, holdout: int, horizon: int) -> dict[str, Any]:
    """Seasonal naive with drift: same calendar month, most recent training year, scaled by
    the training-window annual growth rate. Backtested on the holdout."""
    train = monthly[:-holdout]
    years = sorted(int(y) for y in train.index.year)
    first_total = float(train[train.index.year == years[0]].sum())
    last_total = float(train[train.index.year == years[-1]].sum())
    n_years = years[-1] - years[0]
    drift = (last_total / first_total) ** (1.0 / n_years) if n_years > 0 and first_total > 0 else 1.0

    ref_year = train[train.index.year == years[-1]]
    ref_by_month = {int(m): float(v) for m, v in zip(ref_year.index.month, ref_year.values)}

    hold = monthly[-holdout:]
    preds = np.array([ref_by_month.get(int(m), float(np.nan)) * drift for m in hold.index.month])
    actual = hold.values
    mape = float(np.mean(np.abs((preds - actual) / actual)) * 100.0)
    bias = float(np.mean((preds - actual) / actual) * 100.0)

    last_year = monthly[monthly.index.year == monthly.index.year.max()]
    fc = np.array([float(v) * drift for v in last_year.values])[:horizon]
    # Widened naive interval from holdout residuals (80% band)
    resid_pct = np.abs((preds - actual) / actual)
    band = float(np.quantile(resid_pct, 0.8))
    return {"forecast": fc, "lower": fc * (1 - band), "upper": fc * (1 + band), "mape": mape, "bias": bias, "drift": drift}


def forecast_monthly_sales(df: pd.DataFrame, horizon: int = 12, holdout_months: int = 12) -> dict[str, Any]:
    """Forecast monthly sales, selecting between two candidate models by holdout MAPE.

    Candidate A (seasonal naive with drift) repeats the most recent observed year scaled by
    the training-window growth rate. Candidate B extrapolates a damped log-linear trend with
    multiplicative month seasonality. Both are backtested on the trailing `holdout_months`;
    the lower-MAPE candidate produces the forward forecast.

    Args:
        df: Order-line DataFrame with 'Order Date' and 'Sales'.
        horizon: Months to forecast beyond the last observed month.
        holdout_months: Trailing months held out for backtest validation.

    Returns:
        Dictionary with history, both candidates' metrics, the winning forecast with an
        80% interval, and FY totals.
    """
    monthly = df.set_index("Order Date").resample("MS")["Sales"].sum().astype(float)
    n = len(monthly)
    if n < holdout_months + 12:
        return {"error": "Not enough monthly history to fit the models."}

    naive = _seasonal_naive_drift_forecast(monthly, holdout_months, horizon)
    trend = _damped_trend_forecast(monthly, holdout_months, horizon)

    candidates = {
        "A: Seasonal naive with drift": naive,
        "B: Damped log-linear trend": trend,
    }
    chosen_name = min(candidates, key=lambda k: candidates[k]["mape"])
    chosen = candidates[chosen_name]

    f_dates = pd.date_range(monthly.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    history = pd.DataFrame(
        {
            "date": monthly.index,
            "actual": monthly.values,
            "fitted": monthly.values,  # naive model has no fitted line; chart plots actuals
        }
    )
    forecast = pd.DataFrame(
        {"date": f_dates, "forecast": chosen["forecast"], "lower_80": chosen["lower"], "upper_80": chosen["upper"]}
    )

    actual_fy = float(monthly[monthly.index.year == monthly.index.year.max()].sum())
    forecast_fy = float(chosen["forecast"].sum())

    return {
        "history": history,
        "forecast": forecast,
        "model_used": chosen_name,
        "candidate_metrics": {name: {"mape_pct": c["mape"], "bias_pct": c["bias"]} for name, c in candidates.items()},
        "drift": naive["drift"],
        "backtest_mape_pct": chosen["mape"],
        "backtest_bias_pct": chosen["bias"],
        "forecast_fy_total": forecast_fy,
        "last_actual_fy_total": actual_fy,
        "fy_growth_pct": (forecast_fy / actual_fy - 1.0) * 100.0 if actual_fy > 0 else 0.0,
    }


# ---------------------------------------------------------------------------
# Model 2: Discount-demand response (controlled OLS on log quantity)
# ---------------------------------------------------------------------------

_RESPONSE_LEVELS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]


def _response_design(frame: pd.DataFrame) -> pd.DataFrame:
    """Build the controlled design matrix (reference levels dropped for dummies)."""
    cols: dict[str, np.ndarray] = {
        "discount": frame["Discount"].to_numpy(dtype=float),
        "discount_sq": frame["Discount"].to_numpy(dtype=float) ** 2,
    }
    for col in ["Category", "Market", "Year", "month"]:
        levels = sorted(frame[col].unique(), key=str)
        for level in levels[1:]:
            cols[f"{col}_{level}"] = (frame[col].astype(str) == str(level)).to_numpy(dtype=float)
    return pd.DataFrame(cols, index=frame.index)


def analyze_discount_response(
    df: pd.DataFrame, holdout_frac: float = 0.2, seed: int = 42, caps: list[float] | None = None
) -> dict[str, Any]:
    """Estimate how line volume responds to discount depth, controlling for product,
    market, year, and month (Q4 seasonality is the key confounder).

    Args:
        df: Order-line DataFrame.
        holdout_frac: Random share of lines held out for validation.
        seed: RNG seed for the holdout split.
        caps: Discount caps to measure volume retention at. Defaults to [0.15, 0.20, 0.25].

    Returns:
        Dictionary with the response curve (volume index vs discount, 0% = 100),
        implied volume retention under discount caps, and holdout error.
    """
    cap_list = caps if caps is not None else [0.15, 0.20, 0.25]
    d = df[["Quantity", "Discount", "Category", "Market", "Year", "Order Date"]].dropna().copy()
    d["month"] = d["Order Date"].dt.month
    d = d[d["Discount"] <= 0.85]
    rng = np.random.default_rng(seed)
    test_mask = rng.random(len(d)) < holdout_frac

    X_all = _response_design(d)
    y_all = np.log(d["Quantity"].to_numpy(dtype=float) + 1.0)

    beta_tr, *_ = np.linalg.lstsq(X_all[~test_mask].to_numpy(dtype=float), y_all[~test_mask], rcond=None)
    pred_test = X_all[test_mask].to_numpy(dtype=float) @ beta_tr
    mae_log = float(np.mean(np.abs(pred_test - y_all[test_mask])))

    beta, *_ = np.linalg.lstsq(X_all.to_numpy(dtype=float), y_all, rcond=None)

    # Response curve evaluated on the reference profile (reference category/market/year/month)
    base_levels: dict[str, Any] = {
        col: sorted(d[col].unique(), key=str)[0] for col in ["Category", "Market", "Year", "month"]
    }
    curve_rows = []
    for level in _RESPONSE_LEVELS:
        row = d.iloc[[0]].copy()
        row["Discount"] = level
        row["Category"], row["Market"], row["Year"], row["month"] = (
            base_levels["Category"], base_levels["Market"], base_levels["Year"], base_levels["month"],
        )
        curve_rows.append(_response_design(row).reindex(columns=X_all.columns, fill_value=0.0))
    curve_X = pd.concat(curve_rows, ignore_index=True).to_numpy(dtype=float)
    preds_log = curve_X @ beta
    baseline = preds_log[0]
    curve = [
        {"discount": level, "volume_index": float(np.exp(p - baseline) * 100.0)}
        for level, p in zip(_RESPONSE_LEVELS, preds_log)
    ]

    # Implied volume retention when affected lines are capped (their own dummies held fixed)
    retention = []
    for cap in cap_list:
        affected = d[d["Discount"] > cap]
        if affected.empty:
            retention.append({"cap": cap, "retained_pct": 100.0, "affected_lines": 0})
            continue
        Xa = _response_design(affected).reindex(columns=X_all.columns, fill_value=0.0).to_numpy(dtype=float)
        Xc = Xa.copy()
        Xc[:, 0] = cap
        Xc[:, 1] = cap * cap
        q_actual = np.exp(Xa @ beta)
        q_capped = np.exp(Xc @ beta)
        retention.append(
            {
                "cap": cap,
                "retained_pct": float(q_capped.sum() / q_actual.sum() * 100.0),
                "affected_lines": int(len(affected)),
            }
        )

    return {
        "curve": curve,
        "retention": retention,
        "holdout_mae_log": mae_log,
        "n_lines": int(len(d)),
        "discount_coef": float(beta[0]),
        "discount_sq_coef": float(beta[1]),
    }


# ---------------------------------------------------------------------------
# Model 3: Customer churn (lapse) risk scoring
# ---------------------------------------------------------------------------

_CHURN_FEATURES = [
    "n_orders",
    "recency_days",
    "avg_discount",
    "share_lines_over_20pct",
    "avg_order_value",
    "log_total_sales",
]


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def _fit_logistic(X: np.ndarray, y: np.ndarray, l2: float = 1.0, iters: int = 25) -> np.ndarray:
    """L2-regularised logistic regression via Newton-Raphson on standardised features."""
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        p = _sigmoid(X @ beta)
        grad = X.T @ (p - y) + l2 * beta
        W = np.clip(p * (1 - p), 1e-6, None)
        H = X.T @ (X * W[:, None]) + l2 * np.eye(X.shape[1])
        step = np.linalg.solve(H, grad)
        beta_new = beta - step
        if np.max(np.abs(beta_new - beta)) < 1e-8:
            beta = beta_new
            break
        beta = beta_new
    return beta


def _auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    """Rank-based AUC (Mann-Whitney), tie-aware."""
    ranks = pd.Series(scores).rank().to_numpy()
    npos = float((y_true == 1).sum())
    nneg = float((y_true == 0).sum())
    if npos == 0 or nneg == 0:
        return 0.5
    return float((ranks[y_true == 1].sum() - npos * (npos + 1) / 2.0) / (npos * nneg))


def score_customer_churn_risk(
    df: pd.DataFrame, feature_cutoff: str = "2013-12-31", test_frac: float = 0.25, seed: int = 42
) -> dict[str, Any]:
    """Score every customer's probability of lapsing (no orders in the year after the cutoff).

    Features come only from behaviour before `feature_cutoff` (so recency is a legitimate
    predictor, not leakage); the label is the absence of any order in the following year.

    Args:
        df: Order-line DataFrame with 'Customer ID', 'Order Date', 'Discount', 'Sales'.
        feature_cutoff: Last date of the feature window.
        test_frac: Share of customers held out for AUC validation.
        seed: RNG seed for the customer-level split.

    Returns:
        Dictionary with AUC, lapse rate, feature effects, and per-customer scores.
    """
    cutoff = pd.Timestamp(feature_cutoff)
    pre = df[df["Order Date"] <= cutoff]
    post = df[df["Order Date"] > cutoff]
    if pre.empty:
        return {"error": "No orders before the feature cutoff."}

    grp = pre.groupby("Customer ID")
    orders_per_customer = grp["Order ID"].nunique()
    feats = pd.DataFrame(
        {
            "n_orders": orders_per_customer,
            "recency_days": (cutoff - grp["Order Date"].max()).dt.days,
            "avg_discount": grp["Discount"].mean(),
            "share_lines_over_20pct": pre.assign(o20=pre["Discount"] > 0.2).groupby("Customer ID")["o20"].mean(),
            "avg_order_value": grp["Sales"].sum() / orders_per_customer,
            "log_total_sales": np.log1p(grp["Sales"].sum()),
        }
    )
    post_customers = set(post["Customer ID"].unique())
    feats["lapsed"] = [0 if cid in post_customers else 1 for cid in feats.index]
    feats["pre_sales"] = grp["Sales"].sum()

    rng = np.random.default_rng(seed)
    test_mask = rng.random(len(feats)) < test_frac

    X_raw = feats[_CHURN_FEATURES].to_numpy(dtype=float)
    mu, sd = X_raw.mean(axis=0), X_raw.std(axis=0)
    sd[sd == 0] = 1.0
    X_std = (X_raw - mu) / sd
    X_design = np.column_stack([np.ones(len(X_std)), X_std])

    beta_tr = _fit_logistic(X_design[~test_mask], feats["lapsed"].to_numpy()[~test_mask])
    p_test = _sigmoid(X_design[test_mask] @ beta_tr)
    auc_test = _auc(feats["lapsed"].to_numpy()[test_mask], p_test)

    beta_full = _fit_logistic(X_design, feats["lapsed"].to_numpy())
    feats["p_lapse"] = _sigmoid(X_design @ beta_full)
    # Quantile tiers instead of fixed probability cutoffs: with a ~5% lapse rate, almost no
    # customer crosses 0.5, so rank-based tiers keep the top tier meaningful
    feats["risk_tier"] = pd.qcut(
        feats["p_lapse"].rank(method="first"),
        q=3,
        labels=["Low (bottom third)", "Medium (middle third)", "High (top third)"],
    )

    effects = pd.DataFrame({"feature": _CHURN_FEATURES, "logistic_coef": beta_full[1:]})

    return {
        "auc_test": auc_test,
        "lapse_rate_pct": float(feats["lapsed"].mean() * 100.0),
        "n_customers": int(len(feats)),
        "feature_effects": effects,
        "customer_scores": feats.reset_index().rename(columns={"index": "Customer ID"}),
        "feature_cutoff": feature_cutoff,
    }
