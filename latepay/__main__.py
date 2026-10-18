import argparse

from .model import LatePayModel
from .synth import make_invoices


def main():
    p = argparse.ArgumentParser(prog="latepay")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="run on synthetic data and print the arena report")
    r = sub.add_parser("report", help="train on a CSV of invoices and forecast the unpaid ones")
    r.add_argument("csv", help="columns: invoice_id,customer,amount,issue_date,due_date,paid_date (empty = unpaid)")
    r.add_argument("--out", default="forecast.csv")
    a = p.parse_args()
    if a.cmd == "demo":
        m = LatePayModel().fit(make_invoices())
        print(m.report)
    else:
        import pandas as pd
        df = pd.read_csv(a.csv)
        m = LatePayModel().fit(df)
        print(m.report)
        open_ = df[df["paid_date"].isna()]
        m.predict(open_).to_csv(a.out, index=False)
        print(f"{len(open_)} open invoices -> {a.out}")


main()
