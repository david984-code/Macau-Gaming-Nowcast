"""Unit tests for the DICJ GGR XML parser (no network)."""

import pandas as pd

from src.data import dicj

_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<STATISTICS><REPORT><DATA><RECORD>
  <DATA css="formheading">Jan</DATA><DATA>22,633</DATA><DATA>18,254</DATA><DATA>24.0%</DATA>
</RECORD><RECORD>
  <DATA css="formheading">Feb</DATA><DATA>20,627</DATA><DATA>19,744</DATA><DATA>4.5%</DATA>
</RECORD><RECORD>
  <DATA css="formheading">Total</DATA><DATA>43,260</DATA><DATA>37,998</DATA><DATA>13.9%</DATA>
</RECORD></DATA></REPORT></STATISTICS>"""


def test_parse_extracts_current_year_monthly_ggr():
    out = dicj._parse(_SAMPLE, 2026)
    assert out[pd.Timestamp(2026, 1, 1)] == 22633.0  # comma stripped, current-year col
    assert out[pd.Timestamp(2026, 2, 1)] == 20627.0
    assert pd.Timestamp(2026, 3, 1) not in out  # "Total" row is not a month


def test_parse_ignores_non_month_and_blank_rows():
    bad = b"<STATISTICS><RECORD><DATA>Jan</DATA><DATA></DATA></RECORD></STATISTICS>"
    assert dicj._parse(bad, 2026) == {}
