"""Scraper for Austrian (AT) bank codes from OeNB.

Source: OeNB SEPA-ZV-VZ CSV
URL:    https://www.oenb.at/docroot/downloads_observ/sepa-zv-vz_gesamt.csv
"""

import csv
import io
import json
import sys
from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent.parent / "src" / "iban_tools" / "data"

ALLOWED_SECTORS = {"Raiffeisen", "Aktienbanken", "§ 9 Institute", "Sparkassen", "Volksbanken"}


def scrape_at() -> dict[str, str]:
    """Scrape Austrian bank code → BIC mapping from OeNB."""
    url = "https://www.oenb.at/docroot/downloads_observ/sepa-zv-vz_gesamt.csv"
    print(f"[AT] Downloading CSV from {url}...")

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    content = resp.content.decode("iso-8859-1")

    # Skip lines until we find the header row starting with "Kennzeichen;"
    lines = content.split("\n")
    header_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("Kennzeichen;"):
            header_idx = i
            break

    csv_content = "\n".join(lines[header_idx:])
    reader = csv.DictReader(io.StringIO(csv_content), delimiter=";")

    bank_codes: dict[str, str] = {}
    for row in reader:
        sector = row.get("Sektor", "").strip()
        if sector not in ALLOWED_SECTORS:
            continue

        blz = row.get("Bankleitzahl", "").strip()
        bic = row.get("SWIFT-Code", "").strip()

        if blz and bic:
            bank_codes[blz] = bic

    print(f"[AT] Found {len(bank_codes)} bank codes.")
    return bank_codes


def main():
    data = scrape_at()
    if data:
        output = DATA_DIR / "at.json"
        with output.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"[AT] Written to {output}")
    else:
        print("[AT] No data scraped, keeping existing file.", file=sys.stderr)


if __name__ == "__main__":
    main()
