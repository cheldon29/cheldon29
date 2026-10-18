import numpy as np

from latepay import LatePayModel, make_invoices


def test_arena_runs_and_beats_baseline_on_structured_data():
    m = LatePayModel().fit(make_invoices(seed=1, amount_effect=6.0))
    assert m.report.model_wins
    assert abs(m.report.coverage - 0.8) < 0.08


def test_abstains_on_pure_noise():
    df = make_invoices(seed=2)
    rng = np.random.default_rng(0)
    # destroy signal: random lateness unrelated to customer or amount
    df["paid_date"] = df["due_date"] + (rng.normal(0, 20, len(df))).round().astype(int).astype("timedelta64[D]")
    m = LatePayModel().fit(df)
    assert not m.report.model_wins
    assert (m.predict(df.tail(20))["status"] != "forecast").all()


def test_no_leakage_in_history_features():
    from latepay.model import _history_features, _prepare
    df = _prepare(make_invoices(n=300, seed=3))
    X = _history_features(df, df)
    assert X["n_hist"].iloc[0] == 0


def test_short_history_abstains():
    df = make_invoices(seed=4)
    m = LatePayModel().fit(df)
    new = df.tail(1).copy()
    new["customer"] = "NEW"
    new["paid_date"] = None
    assert m.predict(new)["status"].iloc[0].startswith("abstain")


def test_audit_report_renders():
    from latepay.audit import build_audit
    df = make_invoices(n=600, seed=5, amount_effect=6.0)
    df.loc[df.index[-20:], "paid_date"] = None
    md = build_audit(df, "Acme")
    assert "Late-payment audit — Acme" in md and "Top" in md


def test_intervals_inflated_to_target_coverage():
    m = LatePayModel().fit(make_invoices(seed=1, amount_effect=6.0))
    assert m.report.coverage >= 0.78
