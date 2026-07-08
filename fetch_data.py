#!/usr/bin/env python3
"""Fetch daily adjusted closes + dollar volume for the tracker universe.

Reads universe.json (single source of truth shared with index.html),
writes data.json = {"asof": "...", "dates": [...], "series": {TICKER: {"c": [...], "dv": [...]}}}

Run by .github/workflows/update-data.yml every US trading day.
"""
import json
import math
import sys
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

KEEP_DAYS = 220          # trading days kept in data.json (needs >= 63 for SMA63 + 8x5 tail)
FETCH_PERIOD = "420d"    # calendar-day fetch window with buffer


def load_universe(path="universe.json"):
    with open(path) as f:
        u = json.load(f)
    tickers = {u["bench"], *u["sectors"]}
    for t in u["themes"]:
        tickers.update(t["stocks"])
    return u, sorted(tickers)


def clean(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else x


def main():
    u, tickers = load_universe()
    print(f"universe: {len(tickers)} tickers, bench={u['bench']}")

    df = yf.download(
        tickers,
        period=FETCH_PERIOD,
        interval="1d",
        auto_adjust=True,      # total-return-adjusted close
        group_by="ticker",
        threads=True,
        progress=False,
    )
    if df.empty:
        print("ERROR: yfinance returned empty frame", file=sys.stderr)
        sys.exit(1)

    # align on benchmark's trading calendar
    bench = u["bench"]
    bench_close = df[bench]["Close"].dropna() if bench in df.columns.get_level_values(0) else None
    if bench_close is None or len(bench_close) < 100:
        print(f"ERROR: benchmark {bench} has insufficient data", file=sys.stderr)
        sys.exit(1)

    dates = bench_close.index[-KEEP_DAYS:]
    series, missing = {}, []
    for t in tickers:
        try:
            sub = df[t][["Close", "Volume"]].reindex(dates)
        except KeyError:
            missing.append(t)
            continue
        c = sub["Close"]
        if c.notna().sum() < 70:   # not enough history to compute SMA63 metrics
            missing.append(t)
            continue
        dv = (sub["Close"] * sub["Volume"]).round(0)
        series[t] = {
            "c": [clean(round(v, 4)) if pd.notna(v) else None for v in c],
            "dv": [clean(v) if pd.notna(v) else None for v in dv],
        }

    out = {
        "asof": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "dates": [d.strftime("%Y-%m-%d") for d in dates],
        "series": series,
    }
    with open("data.json", "w") as f:
        json.dump(out, f, separators=(",", ":"))

    size_kb = len(json.dumps(out, separators=(",", ":"))) / 1024
    print(f"data.json: {len(dates)} days x {len(series)} tickers ({size_kb:.0f} KB)")
    if missing:
        print(f"skipped (no/short data): {', '.join(missing)}")


if __name__ == "__main__":
    main()
