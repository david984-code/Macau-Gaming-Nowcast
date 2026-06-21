"""The nowcast test: does Macau GGR growth lead operator revenue growth?

Same honest-numbers bar as the sibling readers: headline is the contemporaneous
(lag-0) correlation of *deseasonalized QoQ growth* (not co-trend-inflated
levels-of-YoY), with a paired 2-quarter block-bootstrap CI. The structural
prediction: Macau-heavy operators (LVS/MLCO/WYNN) track GGR; US-heavy MGM doesn't.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

import config

from .analysis import ggr_quarterly, operator_revenue

_N_BOOT = 5000
_BLOCK = 2


def _deseasonalized_growth(s: pd.Series) -> pd.Series:
    s = s.dropna()
    if len(s) < 10:
        return pd.Series(dtype=float, index=pd.DatetimeIndex([]))
    y = np.log(s.to_numpy())
    q = pd.DatetimeIndex(s.index).quarter
    dummies = np.column_stack([(q == k).astype(float) for k in (2, 3, 4)])
    x = np.column_stack([np.ones(len(y)), np.arange(len(y)), dummies])
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return pd.Series(np.diff(y - dummies @ beta[2:]), index=s.index[1:])


def _block_bootstrap_ci(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    rng = np.random.default_rng(0)
    m = len(a)
    pool = np.arange(m - _BLOCK + 1)
    rs = np.empty(_N_BOOT)
    for i in range(_N_BOOT):
        idx = np.concatenate(
            [np.arange(s, s + _BLOCK) for s in rng.choice(pool, int(np.ceil(m / _BLOCK)))]
        )[:m]
        aa, bb = a[idx], b[idx]
        rs[i] = np.corrcoef(aa, bb)[0, 1] if aa.std() and bb.std() else 0.0
    rs = rs[~np.isnan(rs)]
    lo, hi = np.percentile(rs, [2.5, 97.5])
    return float(lo), float(hi), float(2 * min((rs <= 0).mean(), (rs >= 0).mean()))


def _bridge(label: str, ggr: pd.Series, rev: pd.Series, since: str | None) -> dict:
    common = ggr.index.intersection(rev.index)
    # Deseasonalize on the FULL overlap (robust seasonal estimate), then restrict
    # the correlation window -- pre-reopening Macau (2020-22 border closures) is a
    # distorted regime we don't want to score on.
    gg = _deseasonalized_growth(ggr.loc[common])
    gr = _deseasonalized_growth(rev.loc[common])
    pair = pd.DataFrame({"g": gg, "r": gr}).dropna()  # lag-0 nowcast
    if since:
        pair = pair[pair.index >= since]
    res: dict = {"label": label, "n": len(pair)}
    if len(pair) >= 6:
        r = float(pair["g"].corr(pair["r"]))
        lo, hi, p = _block_bootstrap_ci(pair["g"].to_numpy(), pair["r"].to_numpy())
        res.update(r=r, ci95=[lo, hi], p_value=p, signal=bool(lo > 0 or hi < 0))
    return res


def run(since: str = "2022-09-30") -> list[dict]:
    """Bridge each operator; default window is the post-COVID Macau reopening."""
    ggr = ggr_quarterly()
    rev = operator_revenue()
    results = []
    for t in config.OPERATORS:
        if t in rev.columns:
            results.append(_bridge(t, ggr, rev[t].dropna(), since))
    print(f"Macau GGR -> operator revenue (deseasonalized QoQ growth, since {since})")
    print("=" * 60)
    for r in results:
        if "r" in r:
            flag = "SIGNAL" if r["signal"] else "none"
            print(
                f"  {r['label']:5} r={r['r']:+.2f}  CI=[{r['ci95'][0]:+.2f},{r['ci95'][1]:+.2f}]"
                f"  n={r['n']:>2}  {flag}"
            )
        else:
            print(f"  {r['label']:5} insufficient history (n={r['n']})")
    (config.OUTPUT_DIR / "nowcast_results.json").write_text(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    run()
