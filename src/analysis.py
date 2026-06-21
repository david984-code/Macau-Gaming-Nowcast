"""Quarterly Macau GGR and the operator-revenue alignment."""

from __future__ import annotations

import pandas as pd

from .data import dicj, sec_xbrl


def ggr_quarterly(force: bool = False) -> pd.Series:
    """Macau GGR summed to complete calendar quarters (MOP million)."""
    m = dicj.fetch(force=force)
    quarter = pd.DatetimeIndex(m.index).to_period("Q")
    counts = m.groupby(quarter).count()
    q = m.groupby(quarter).sum()
    q = q[counts == 3]  # complete quarters only
    q.index = pd.PeriodIndex(q.index).to_timestamp(how="end").normalize()
    return q


def operator_revenue(force: bool = False) -> pd.DataFrame:
    return sec_xbrl.fetch(force=force)


if __name__ == "__main__":
    g = ggr_quarterly()
    print(f"GGR quarterly: {g.index.min().date()} -> {g.index.max().date()} ({len(g)})")
    print(g.tail(4).map(lambda v: f"{v:,.0f}"))
