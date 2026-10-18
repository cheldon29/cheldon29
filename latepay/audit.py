"""Turn a client's invoice CSV into a client-ready markdown audit report."""
import pandas as pd

from .model import LatePayModel


def build_audit(df, client="Client", top=10):
    m = LatePayModel().fit(df)
    r = m.report
    open_ = df[df["paid_date"].isna()]
    fc = m.predict(open_) if len(open_) else pd.DataFrame()
    ok = fc[fc["status"] == "forecast"] if len(fc) else fc
    lines = [f"# Late-payment audit — {client}", ""]
    lines += ["## Can we trust the forecast?", "", "```", str(r), "```", ""]
    if r.coverage < r.target_coverage - 0.05:
        lines += [f"> Intervals fall short of target coverage ({r.coverage:.0%}); treat them as optimistic.", ""]
    if not r.model_wins:
        lines += ["**Result: not predictable enough to beat a simple rule.** We recommend the baseline rule "
                  "(each customer's median past lateness) rather than a model.", ""]
    lines += [f"Open invoices: {len(open_)} · forecast: {len(ok)} · withheld: {len(open_) - len(ok)}", ""]
    if len(ok):
        risky = ok.sort_values(["p_late", "amount"], ascending=False).head(top)
        at_risk = float((ok["amount"] * ok["p_late"]).sum())
        lines += [f"Expected amount paid late: **{at_risk:,.0f}** of {ok['amount'].sum():,.0f} forecast.", "",
                  f"## Top {len(risky)} invoices to chase", "", risky[["invoice_id", "customer", "amount", "p_late",
                  "pred_days_late", "low", "high"]].to_markdown(index=False), ""]
    lines += ["## Method", "", "Walk-forward test on this client's own history; forecasts withheld where the model "
              "does not beat the baseline or the customer has under 3 paid invoices. Estimates, not facts."]
    return "\n".join(lines)
