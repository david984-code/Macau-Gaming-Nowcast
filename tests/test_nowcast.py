"""Unit tests for the nowcast statistics (no network)."""

import numpy as np
import pandas as pd

from src import nowcast as nc


def _q_index(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2010-03-31", periods=n, freq="QE")


def test_deseasonalized_growth_strips_seasonality_and_trend():
    idx = _q_index(24)
    seasonal = np.array([1.0, 1.4, 0.7, 1.2])[(idx.quarter - 1)]
    vals = np.exp(0.02 * np.arange(24)) * seasonal
    g = nc._deseasonalized_growth(pd.Series(vals, index=idx))
    assert g.std() < 1e-9
    assert abs(g.mean() - 0.02) < 1e-6


def test_deseasonalized_growth_needs_min_history():
    assert nc._deseasonalized_growth(pd.Series([1, 2, 3], index=_q_index(3))).empty


def test_block_bootstrap_ci_perfect_corr_and_independent():
    rng = np.random.default_rng(1)
    a = rng.normal(size=40)
    lo, hi, p = nc._block_bootstrap_ci(a, a.copy())
    assert lo > 0.9 and p < 0.05
    lo2, hi2, p2 = nc._block_bootstrap_ci(a, rng.normal(size=40))
    assert lo2 < 0 < hi2 and p2 > 0.05
