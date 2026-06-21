"""Operator quarterly revenue from SEC XBRL company-concept facts (structured)."""

from __future__ import annotations

import pandas as pd
import requests

import config

from . import cache
from .net import network_retry

_API = "https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{concept}.json"
_CONCEPTS = ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax")
_HEADERS = {"User-Agent": config.SEC_UA}


@network_retry
def _concept(cik: int, concept: str) -> list[dict]:
    r = requests.get(_API.format(cik=cik, concept=concept), headers=_HEADERS, timeout=30)
    if r.status_code != 200:
        return []
    return r.json().get("units", {}).get("USD", [])


def _quarterly_revenue(cik: int) -> pd.Series:
    """Best available quarterly revenue series (~3-month facts), by period end."""
    best = pd.Series(dtype=float)
    for concept in _CONCEPTS:
        rows = [u for u in _concept(cik, concept) if "start" in u]
        if not rows:
            continue
        df = pd.DataFrame(rows)
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        df["days"] = (df["end"] - df["start"]).dt.days
        sub = df[(df["days"] >= 80) & (df["days"] <= 100)].drop_duplicates("end")
        q = sub.set_index("end")["val"].sort_index().resample("QE").last()
        if len(q) > len(best):
            best = q
    return best


def fetch(force: bool = False) -> pd.DataFrame:
    """Quarterly revenue ($) per operator, period-end indexed."""
    if not force and cache.is_fresh("operator_revenue"):
        return cache.load("operator_revenue")
    cols = {t: _quarterly_revenue(cik) for t, (cik, _) in config.OPERATORS.items()}
    df = pd.DataFrame(cols).sort_index()
    cache.save("operator_revenue", df)
    return df


if __name__ == "__main__":
    df = fetch(force=True)
    print(df.tail(6).map(lambda v: f"{v / 1e6:,.0f}M" if pd.notna(v) else "-"))
