"""Macau monthly Gross Gaming Revenue from the DICJ regulator (keyless).

The DICJ publishes monthly GGR as a per-year XML file consumed by an XSLT page:
``.../DadosEstat_mensal/<year>/report_en.xml``. Each RECORD is one month with
[month, current-year GGR, prior-year GGR, variance, ...]. Unit: MOP million.
"""

from __future__ import annotations

import datetime as dt
import xml.etree.ElementTree as ET

import pandas as pd
import requests

import config

from . import cache
from .net import network_retry

_URL = "https://www.dicj.gov.mo/web/en/information/DadosEstat_mensal/{year}/report_en.xml"
_HEADERS = {"User-Agent": "Mozilla/5.0 (macau-gaming-nowcast research)"}
_NAME = "macau_ggr"
_MONTHS = {
    m: i
    for i, m in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        start=1,
    )
}


def _parse(xml: bytes, year: int) -> dict[pd.Timestamp, float]:
    """Pure parse of a DICJ report XML -> {month-start: current-year GGR}."""
    out: dict[pd.Timestamp, float] = {}
    for rec in ET.fromstring(xml).iter("RECORD"):
        d = [x.text for x in rec.findall("DATA")]
        if len(d) >= 2 and d[0] in _MONTHS and d[1]:
            try:
                out[pd.Timestamp(year, _MONTHS[d[0]], 1)] = float(d[1].replace(",", ""))
            except ValueError:
                continue
    return out


@network_retry
def _fetch_year(year: int) -> dict[pd.Timestamp, float]:
    r = requests.get(_URL.format(year=year), headers=_HEADERS, timeout=30)
    return _parse(r.content, year) if r.status_code == 200 else {}


def fetch(force: bool = False) -> pd.Series:
    """Monthly Macau GGR (MOP million), month-start index, since GGR_START_YEAR."""
    if not force and cache.is_fresh(_NAME):
        return cache.load(_NAME)["ggr"]
    data: dict[pd.Timestamp, float] = {}
    for year in range(config.GGR_START_YEAR, dt.date.today().year + 1):
        data.update(_fetch_year(year))
    s = pd.Series(data).sort_index()
    s.index.name = "date"
    cache.save(_NAME, s.to_frame("ggr"))
    return s


if __name__ == "__main__":
    s = fetch(force=True)
    print(f"Macau GGR: {s.index.min().date()} -> {s.index.max().date()}, {len(s)} months")
    print(s.tail(6).map(lambda v: f"{v:,.0f} MOP mn"))
