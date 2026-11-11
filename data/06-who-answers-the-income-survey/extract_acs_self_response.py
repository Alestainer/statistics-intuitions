"""Build acs-self-response-by-tract-income.csv from the Census Bureau's 2026 Planning Database.

Source file (200 MB): https://www2.census.gov/adrm/PDB/2026/pdb2026tr.csv
Usage: uv run python extract_acs_self_response.py path/to/pdb2026tr.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS = {
    "Med_HHD_Inc_ACS_20_24": "income",
    "pct_Prs_Blw_Pov_Lev_ACS_20_24": "poverty",
    "pct_Renter_Occp_HU_ACS_20_24": "renters",
    "Tot_Occp_Units_ACS_20_24": "units",
    "Self_Response_Rate_ACS_20_24": "self_response",
}
MIN_UNITS = 100
GROUPS = 10

raw = pd.read_csv(sys.argv[1], usecols=list(COLUMNS), dtype=str, encoding="latin-1")
tracts = pd.DataFrame()
for source, name in COLUMNS.items():
    values = pd.to_numeric(raw[source].str.replace(r"[$,+]", "", regex=True), errors="coerce")
    tracts[name] = values.where((values >= 0) & (values <= 5_000_000))  # negative values are missing-data codes
tracts = tracts.dropna()
tracts = tracts[(tracts.units >= MIN_UNITS) & (tracts.self_response > 0)].sort_values("income")
tracts["group"] = np.minimum(GROUPS - 1, (tracts.units.cumsum() / tracts.units.sum() * GROUPS).astype(int)) + 1

def weighted(group, column):
    return np.average(group[column], weights=group.units)

rows = [
    {
        "income_group": number,
        "tracts": len(group),
        "occupied_units": int(group.units.sum()),
        "median_household_income": round(weighted(group, "income")),
        "self_response_rate": round(weighted(group, "self_response"), 1),
        "poverty_rate": round(weighted(group, "poverty"), 1),
        "renter_share": round(weighted(group, "renters"), 1),
    }
    for number, group in tracts.groupby("group")
]
output = Path(__file__).with_name("acs-self-response-by-tract-income.csv")
pd.DataFrame(rows).to_csv(output, index=False)
print(f"{len(tracts):,} tracts used -> {output.name}")
