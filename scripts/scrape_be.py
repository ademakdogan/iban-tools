"""Scraper for Belgian (BE) bank codes from NBB.

Source: National Bank of Belgium full list XLSX
URL:    https://www.nbb.be/doc/be/be/protocol/r_fulllist_of_codes_current.xlsx
"""

import json
import sys
from pathlib import Path

import openpyxl
import requests

DATA_DIR = Path(__file__).parent.parent / "src" / "iban_tools" / "data"

PLACEHOLDER_BICS = {"VRIJ", "VRIJ-LIBRE", "nav", "NAV", "NAP", "NYA", "-"}


def scrape_be() -> dict[str, str]:
    """Scrape Belgian bank code → BIC mapping from NBB."""
    url = "https://www.nbb.be/doc/be/be/protocol/r_fulllist_of_codes_current.xlsx"
    print(f"[BE] Downloading XLSX from {url}...")

    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    wb = openpyxl.load_workbook(filename=__import__("io").BytesIO(resp.content), read_only=True)
    ws = wb["Q_FULL_LIST_XLS_REPORT"]

    bank_codes: dict[str, str] = {}
    rows = list(ws.iter_rows(min_row=3, values_only=True))  # Skip header rows

    for row in rows:
        if not row[0]:
            continue

        code = str(row[0]).strip()
        bic = str(row[1]).strip().replace(" ", "") if row[1] else ""

        # Skip placeholder BICs
        if bic in PLACEHOLDER_BICS or not bic:
            continue

        bank_codes[code] = bic

    wb.close()
    print(f"[BE] Found {len(bank_codes)} bank codes.")
    return bank_codes


def main():
    data = scrape_be()
    if data:
        output = DATA_DIR / "be.json"
        with output.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"[BE] Written to {output}")
    else:
        print("[BE] No data scraped, keeping existing file.", file=sys.stderr)


if __name__ == "__main__":
    main()
