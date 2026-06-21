# Macau Gaming Nowcast (DICJ GGR → casino operators)

A consumer-sector **subsector reader** for the Consumer L/S book: nowcast the
US-listed casino operators' reported revenue from **Macau monthly Gross Gaming
Revenue (GGR)** — published by the Macau regulator (DICJ), the single number the
sector trades on — available ~6 weeks before operators print. Same honest-numbers
bar as the sibling readers (deseasonalized-growth bridge, block-bootstrap CIs,
lag-0 contemporaneous headline).

## The data (a small win worth noting)

DICJ serves monthly GGR through an XSLT page that *looks* unscrapeable, but the
data is a clean per-year XML file:
`.../DadosEstat_mensal/<year>/report_en.xml`. `src/data/dicj.py` parses it into a
monthly series back to 2010 (181 months) — no key, no browser.

## The finding (deseasonalized QoQ growth, post-reopening 2022Q3+, lag 0)

| Operator | Macau exposure | r | 95% CI | n |
|---|---|---|---|---|
| **LVS** (Sands China) | ~all (sold Las Vegas) | **+0.93** | [+0.91, +0.99] | 11 |
| **MLCO** (Melco) | Macau-dominant | +0.69 | [+0.26, +0.98] | 7 |
| MGM | mostly US; MGM China ~15% | +0.59 | [+0.11, +1.00] | 7 |

**The story — same coverage-matching law as the sibling readers:** Macau GGR
nowcasts the operators *in proportion to their Macau exposure* — tight for the
Macau-pure LVS, weaker/wider for US-heavy MGM. It's the same shape as
TSA→domestic-airlines (not international Delta) and NYC-trips→Uber-*Mobility*
(not Eats-diluted total): match the signal's coverage to the metric's coverage.

> Honest caveats: the clean window is short (Macau's 2020–22 border closures are a
> distorted regime, excluded), so n is small (7–11) and the MLCO/MGM CIs are wide.
> Revenue here is *total* (XBRL), so MGM's positive read partly reflects broad
> post-reopening recovery; the Macau-*segment* target would sharpen the exposure
> contrast. WYNN is pending a revenue-concept gap in its XBRL facts.

## Layout

```
config.py               # operators -> CIK + Macau-exposure notes
src/data/dicj.py        # Macau monthly GGR from the DICJ XML (keyless)
src/data/sec_xbrl.py    # operator quarterly revenue from SEC XBRL facts
src/data/cache.py, net.py
src/analysis.py         # GGR -> complete calendar quarters; operator revenue
src/nowcast.py          # deseasonalized-growth bridge + block-bootstrap CI
```

## Run

```bash
uv run python -m src.data.dicj      # fetch Macau GGR
uv run python -m src.nowcast        # GGR -> operator-revenue bridge
```

## Roadmap

1. ✅ DICJ GGR fetcher (cracked the XML source) + SEC XBRL revenue + bridge.
2. ✅ **Signal:** LVS r=+0.93 (Macau-pure); exposure-matched across operators.
3. ⬜ Macau-**segment** revenue target (sharpens the exposure contrast; recovers WYNN).
4. ⬜ Walk-forward OOS validation + the quality gate (ruff/mypy/pytest, uv.lock, CI),
      mirroring the sibling readers, then publish.

## Part of a series

A free-data **consumer subsector reader** built to a consistent honest-numbers bar:

- **Gaming (this repo)** — Macau GGR → casino operator revenue.
- [Consumer-Gig-Nowcast](https://github.com/david984-code/Consumer-Gig-Nowcast)
  — NYC TLC trips → Uber Mobility GB growth.
- [Airlines-Alt-Data-Nowcast](https://github.com/david984-code/Airlines-Alt-Data-Nowcast)
  — TSA throughput → carrier RPM growth.
- [Hospitality-Alt-Data-Dashboard](https://github.com/david984-code/hospitality-alt-data-dashboard)
  — TSA / BLS / Trends → hotel-franchisor demand.
