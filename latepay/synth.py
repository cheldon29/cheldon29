"""Synthetic invoice generator with known ground truth, to test the pipeline without client data."""
import numpy as np
import pandas as pd


def make_invoices(n=3000, n_customers=60, seed=0, drift_at=None, amount_effect=2.0):
    """Return a DataFrame: invoice_id, customer, amount, issue_date, due_date, paid_date.

    Each customer has its own typical lateness; big invoices pay slower.
    `amount_effect` is days of extra lateness per log-unit of invoice size (0 = size is irrelevant).
    `drift_at` (0..1) makes every customer pay ~10 days later after that fraction
    of the timeline, to exercise regime-change checks.
    """
    rng = np.random.default_rng(seed)
    base = rng.normal(5, 12, n_customers)
    spread = rng.uniform(0.2, 0.7, n_customers)
    terms = rng.choice([15, 30, 45], n_customers, p=[0.2, 0.6, 0.2])
    start = pd.Timestamp("2024-01-01")
    rows = []
    for i in range(n):
        c = rng.integers(n_customers)
        issue = start + pd.Timedelta(days=int(i / n * 700))
        amount = float(np.exp(rng.normal(7.5, 1.0)))
        late = base[c] + amount_effect * np.log(amount / 1800) + rng.normal(0, 1, ) * 12 * spread[c]
        if drift_at is not None and i / n > drift_at:
            late += 10
        due = issue + pd.Timedelta(days=int(terms[c]))
        paid = due + pd.Timedelta(days=int(round(late)))
        rows.append((i, f"C{c:03d}", round(amount, 2), issue, due, paid))
    df = pd.DataFrame(rows, columns=["invoice_id", "customer", "amount", "issue_date", "due_date", "paid_date"])
    return df
