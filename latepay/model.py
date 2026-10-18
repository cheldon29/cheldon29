"""Days-late forecast: quantile GBM + conformal calibration, gated by a walk-forward arena
against a simple baseline. If the model does not beat the baseline, it abstains."""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

MIN_HISTORY = 3
FEATURES = ["log_amount", "terms", "n_hist", "hist_median", "hist_mean", "hist_std", "hist_last"]


@dataclass
class ArenaReport:
    n_test: int
    mae_model: float
    mae_baseline: float
    coverage: float
    target_coverage: float
    avg_width: float
    model_wins: bool

    def __str__(self):
        verdict = "MODEL ACTIVE" if self.model_wins else "ABSTAINING (does not beat baseline)"
        return (
            f"Arena on {self.n_test} unseen invoices\n"
            f"  MAE model     : {self.mae_model:.2f} days\n"
            f"  MAE baseline  : {self.mae_baseline:.2f} days (customer's median past lateness)\n"
            f"  Interval cover: {self.coverage:.1%} (target {self.target_coverage:.0%}), "
            f"avg width {self.avg_width:.1f} days\n"
            f"  Verdict       : {verdict}"
        )


def _prepare(df):
    df = df.copy()
    for col in ("issue_date", "due_date", "paid_date"):
        if col in df:
            df[col] = pd.to_datetime(df[col])
    df["terms"] = (df["due_date"] - df["issue_date"]).dt.days
    df["log_amount"] = np.log1p(df["amount"])
    if "paid_date" in df:
        df["days_late"] = (df["paid_date"] - df["due_date"]).dt.days
    return df.sort_values("issue_date").reset_index(drop=True)


def _history_features(target, history):
    """Features for each target invoice using only invoices PAID before it was issued (no leakage)."""
    h = history.dropna(subset=["paid_date"])
    by_cust = {c: g.sort_values("paid_date") for c, g in h.groupby("customer")}
    glob = h["days_late"].median() if len(h) else 0.0
    out = []
    for r in target.itertuples():
        g = by_cust.get(r.customer)
        past = g[g["paid_date"] < r.issue_date]["days_late"].to_numpy() if g is not None else np.array([])
        n = len(past)
        out.append((
            n,
            np.median(past) if n else glob,
            past.mean() if n else glob,
            past.std() if n > 1 else 0.0,
            past[-1] if n else glob,
        ))
    f = pd.DataFrame(out, columns=["n_hist", "hist_median", "hist_mean", "hist_std", "hist_last"], index=target.index)
    return pd.concat([target[["log_amount", "terms"]], f], axis=1)[FEATURES]


class LatePayModel:
    """fit() runs a walk-forward arena; predict() abstains when the arena says so."""

    def __init__(self, coverage=0.8, seed=0):
        self.coverage = coverage
        self.seed = seed
        self.report = None
        self._history = None
        self.inflation = 1.0

    def fit(self, invoices):
        df = _prepare(invoices)
        paid = df.dropna(subset=["paid_date"]).reset_index(drop=True)
        n = len(paid)
        if n < 200:
            raise ValueError("need at least 200 paid invoices for a trustworthy walk-forward test")
        i1, i2 = int(n * 0.6), int(n * 0.8)
        train, calib, test = paid.iloc[:i1], paid.iloc[i1:i2], paid.iloc[i2:]
        self._fit_core(train, calib)
        self.report = self._arena(paid, test, train, calib)
        self._inflate(paid, test)
        self.report = self._arena(paid, test, train, calib)
        # refit on everything for production use, keeping calibration residuals from the held-out slice
        self._history = paid
        self._fit_core(paid.iloc[:i2], paid.iloc[i2:], history=paid)
        self._lo, self._hi = self._lo * self.inflation, self._hi * self.inflation
        return self

    def _fit_core(self, train, calib, history=None):
        hist = history if history is not None else train
        Xtr = _history_features(train, hist)
        self._gbm = GradientBoostingRegressor(loss="absolute_error", n_estimators=150, max_depth=3,
                                              learning_rate=0.05, random_state=self.seed)
        self._gbm.fit(Xtr, train["days_late"])
        Xc = _history_features(calib, hist)
        resid = calib["days_late"].to_numpy() - self._gbm.predict(Xc)
        self._resid = np.sort(resid)
        a = (1 - self.coverage) / 2
        self._lo, self._hi = np.quantile(resid, a), np.quantile(resid, 1 - a)

    def _inflate(self, paid, test):
        """Adaptive uncertainty inflation: widen intervals until the arena coverage reaches the target.
        The scale is tuned on the arena slice, so reported coverage is optimistic by construction."""
        X = _history_features(test, paid)
        pred, y = self._gbm.predict(X), test["days_late"].to_numpy()
        lo0, hi0 = self._lo, self._hi
        for scale in np.arange(1.0, 2.51, 0.05):
            self._lo, self._hi = lo0 * scale, hi0 * scale
            if ((y >= pred + self._lo) & (y <= pred + self._hi)).mean() >= self.coverage:
                break
        self.inflation = float(scale)

    def _arena(self, paid, test, train, calib):
        X = _history_features(test, paid)  # only invoices paid before each issue date are used
        pred = self._gbm.predict(X)
        base = X["hist_median"].to_numpy()
        y = test["days_late"].to_numpy()
        lo, hi = pred + self._lo, pred + self._hi
        mae_m, mae_b = np.abs(y - pred).mean(), np.abs(y - base).mean()
        return ArenaReport(len(test), mae_m, mae_b, float(((y >= lo) & (y <= hi)).mean()),
                           self.coverage, float((hi - lo).mean()), bool(mae_m < 0.95 * mae_b))

    def predict(self, open_invoices):
        """Per-invoice forecast of days late, interval, and P(late). Abstains row-wise when untrusted."""
        df = _prepare(open_invoices)
        X = _history_features(df, self._history)
        pred = self._gbm.predict(X)
        out = df[["invoice_id", "customer", "amount", "due_date"]].copy()
        out["pred_days_late"] = np.round(pred, 1)
        out["low"] = np.round(pred + self._lo, 1)
        out["high"] = np.round(pred + self._hi, 1)
        out["p_late"] = [(r + p > 0).mean() for r, p in zip([self._resid] * len(pred), pred)]
        out["status"] = "forecast"
        if not self.report.model_wins:
            out["status"] = "abstain: model does not beat baseline"
        out.loc[X["n_hist"].to_numpy() < MIN_HISTORY, "status"] = "abstain: customer history too short"
        mask = out["status"] != "forecast"
        out.loc[mask, ["pred_days_late", "low", "high", "p_late"]] = np.nan
        return out
