"""Runtime configuration for the Macau Gaming Nowcast.

Thesis: Macau monthly Gross Gaming Revenue (GGR) -- published by the regulator
(DICJ) -- nowcasts the US-listed casino operators' reported revenue ~6 weeks
before they print. It should track the Macau-heavy names (Sands, Wynn, Melco)
tightly and the US-heavy ones (MGM) weakly -- match signal coverage to exposure.
"""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "outputs"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

CACHE_TTL_HOURS = 24.0
GGR_START_YEAR = 2010  # DICJ report_en.xml coverage

# Operator -> (SEC CIK, Macau exposure note). Revenue pulled from SEC XBRL.
OPERATORS: dict[str, tuple[int, str]] = {
    "LVS": (1300514, "Sands China — ~all revenue is Macau post-2022 (sold Las Vegas)"),
    "MLCO": (1297996, "Melco — Macau + Manila, Macau-dominant"),
    "WYNN": (1174922, "Wynn — Macau (~70%) + Las Vegas + Boston"),
    "MGM": (789570, "MGM — mostly US/Las Vegas; MGM China ~15% (US-diluted)"),
}

SEC_UA = "macau-gaming-nowcast research (set SEC_UA)"
