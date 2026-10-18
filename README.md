# latepay

Forecast how late each open invoice will be, with a calibrated interval, and **abstain** when the model
cannot beat a simple baseline. Part of the plan in [MONETISATION.md](MONETISATION.md).

```
pip install numpy pandas scikit-learn
python -m latepay demo                       # synthetic data + arena report
python -m latepay report invoices.csv        # train on paid invoices, forecast unpaid ones -> forecast.csv
```

CSV columns: `invoice_id, customer, amount, issue_date, due_date, paid_date` (empty `paid_date` = still open).

## How it works
- Features per invoice use only the customer's invoices **paid before it was issued** (no leakage).
- Quantile-style GBM predicts days late; split-conformal residuals give the interval and `p_late`.
- Walk-forward arena (60/20/20 time split): the model is only used if its MAE is >5% better than the customer's median past lateness.
- Rows are also withheld for customers with fewer than 3 paid invoices.

## Known limitations (be honest with clients)
- Measured interval coverage can fall short of target (73.5% vs 80% on the synthetic demo): the calibration slice is older than the test slice. Treat intervals as slightly optimistic until recalibrated on live data.
- Unpaid invoices are excluded from training (no censoring/survival handling yet).
- No drift monitor yet (`make_invoices(drift_at=...)` exists to build one).
- Validated only on synthetic data; real-data results will differ. Never sell accuracy figures from the demo.
