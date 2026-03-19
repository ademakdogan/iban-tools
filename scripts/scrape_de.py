"""Scraper for German (DE) bank codes from Bundesbank.

Source: Bundesbank BLZ CSV file
URL:    https://www.bundesbank.de/de/aufgaben/unbarer-zahlungsverkehr/serviceangebot/bankleitzahlen/download-bankleitzahlen-602592
"""

import csv
import io
import json
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "src" / "iban_tools" / "data"


def scrape_de() -> dict[str, str]:
    """Scrape German bank code → BIC mapping from Bundesbank."""
    print("[DE] Fetching Bundesbank download page...")
    page = requests.get(
        "https://www.bundesbank.de/de/aufgaben/unbarer-zahlungsverkehr/"
        "serviceangebot/bankleitzahlen/download-bankleitzahlen-602592",
        timeout=30,
    )
    page.raise_for_status()

    soup = BeautifulSoup(page.text, "html.parser")

    # Find the CSV download link under "Bankleitzahlendateien ungepackt"
    csv_url = None
    for headline in soup.find_all(class_="linklist__headline"):
        if "ungepackt" in headline.get_text():
            links = headline.parent.find_all("a")
            # Second link is the CSV with semicolons
            for link in links:
                href = link.get("href", "")
                if href.endswith(".csv") or "csv" in href.lower():
                    csv_url = "https://www.bundesbank.de" + href
                    break
            if csv_url:
                break

    if not csv_url:
        print("[DE] ERROR: Could not find CSV download link on Bundesbank page.")
        return {}

    print(f"[DE] Downloading CSV from {csv_url}...")
    resp = requests.get(csv_url, timeout=60)
    resp.raise_for_status()

    # Decode ISO-8859-1
    content = resp.content.decode("iso-8859-1")
    reader = csv.DictReader(io.StringIO(content), delimiter=";")

    bank_codes: dict[str, str] = {}
    for row in reader:
        blz = row.get("Bankleitzahl", "").strip()
        bic = row.get("BIC", "").strip()
        status = row.get("Änderungskennzeichen", "").strip()
        merkmal = row.get("Merkmal", "").strip()

        # Skip deleted entries
        if status == "D":
            continue

        # Prefer the main bank (Merkmal == 1)
        if blz and bic:
            if blz not in bank_codes or merkmal == "1":
                bank_codes[blz] = bic

    print(f"[DE] Found {len(bank_codes)} bank codes.")
    return bank_codes


def main():
    data = scrape_de()
    if data:
        output = DATA_DIR / "de.json"
        with output.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"[DE] Written to {output}")
    else:
        print("[DE] No data scraped, keeping existing file.", file=sys.stderr)


if __name__ == "__main__":
    main()
