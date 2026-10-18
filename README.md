# latepay

Forecast how late each open invoice will be, with a calibrated interval, and **abstain** when the model
cannot beat a simple baseline. Part of the plan in [MONETISATION.md](MONETISATION.md).

```
pip install -r requirements.txt
python -m latepay demo                       # synthetic data + arena report
python -m latepay audit invoices.csv --client "Acme"  # client-ready markdown report
python -m latepay report invoices.csv        # train on paid invoices, forecast unpaid ones -> forecast.csv
```

CSV columns: `invoice_id, customer, amount, issue_date, due_date, paid_date` (empty `paid_date` = still open).

## How it works
- Features per invoice use only the customer's invoices **paid before it was issued** (no leakage).
- Quantile-style GBM predicts days late; split-conformal residuals give the interval and `p_late`.
- Walk-forward arena (60/20/20 time split): the model is only used if its MAE is >5% better than the customer's median past lateness.
- Rows are also withheld for customers with fewer than 3 paid invoices.

## Known limitations (be honest with clients)
- Intervals are widened automatically until the arena coverage reaches the target (adaptive inflation, ~x1.2 on the demo). The factor is tuned on the same test slice, so reported coverage is optimistic; recalibrate on live data.
- Unpaid invoices are excluded from training (no censoring/survival handling yet).
- No drift monitor yet (`make_invoices(drift_at=...)` exists to build one).
- Validated only on synthetic data; real-data results will differ. Never sell accuracy figures from the demo.

Sample input format: `outreach/template.csv`. Prospecting notes: `outreach/TARGETS.md`.
