"""Scraper for Dutch (NL) bank codes from Betaalvereniging.

Source: Betaalvereniging BIC-lijst XLSX
URL:    https://www.betaalvereniging.nl/wp-content/uploads/BIC-lijst-NL.xlsx
"""

import json
import sys
from pathlib import Path

import openpyxl
import requests

DATA_DIR = Path(__file__).parent.parent / "src" / "iban_tools" / "data"


def scrape_nl() -> dict[str, str]:
    """Scrape Dutch bank code → BIC mapping from Betaalvereniging."""
    url = "https://www.betaalvereniging.nl/wp-content/uploads/BIC-lijst-NL.xlsx"
    print(f"[NL] Downloading XLSX from {url}...")

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    wb = openpyxl.load_workbook(filename=__import__("io").BytesIO(resp.content), read_only=True)
    ws = wb["BIC-lijst"]

    bank_codes: dict[str, str] = {}
    # Data starts at row 5 (rows 1-4 are titles/headers)
    rows = list(ws.iter_rows(min_row=5, values_only=True))

    for row in rows:
        if not row[0] or not row[1]:
            continue

        bic = str(row[0]).strip()
        code = str(row[1]).strip()

        if code and bic:
            bank_codes[code] = bic

    wb.close()
    print(f"[NL] Found {len(bank_codes)} bank codes.")
    return bank_codes


def main():
    data = scrape_nl()
    if data:
        output = DATA_DIR / "nl.json"
        with output.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"[NL] Written to {output}")
    else:
        print("[NL] No data scraped, keeping existing file.", file=sys.stderr)


if __name__ == "__main__":
    main()
