"""Extract sheltered and unsheltered counts per local area and year from HUD's workbook.

Source: "2007 - 2025 Point-in-Time Estimates by CoC", linked from
https://www.huduser.gov/portal/datasets/ahar/2025-ahar-part-1-pit-estimates-of-homelessness-in-the-us.html
The site refuses scripted downloads, so save the .xlsb file with a browser first.

    uv run --with pyxlsb python extract_hud_pit.py 2007-2025-PIT-Counts-by-CoC.xlsb hud-pit-counts-by-coc.csv
"""
import csv
import re
import sys

from pyxlsb import open_workbook

COLUMNS = ["Overall Homeless", "Sheltered Total Homeless", "Unsheltered Homeless"]
AREA_CODE = re.compile(r"([A-Z]{2}-\d{3})a?")


def as_int(value):
    return "" if value is None or value == "" else int(value)


def main(workbook_path, csv_path):
    workbook = open_workbook(workbook_path)
    with open(csv_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["year", "coc", "name", "count_type", "overall", "sheltered", "unsheltered"])
        for sheet_name in sorted(name for name in workbook.sheets if name.isdigit()):
            with workbook.get_sheet(sheet_name) as sheet:
                rows = sheet.rows()
                header = [cell.v for cell in next(rows)]
                positions = [header.index(column) for column in COLUMNS]
                count_type = header.index("Count Types") if "Count Types" in header else None
                for row in rows:
                    values = [cell.v for cell in row]
                    match = AREA_CODE.fullmatch(values[0]) if isinstance(values[0], str) else None
                    if not match:
                        continue
                    writer.writerow(
                        [sheet_name, match.group(1), values[1], values[count_type] if count_type is not None else ""]
                        + [as_int(values[position]) for position in positions]
                    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
