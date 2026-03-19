"""Scraper for French (FR) and Spanish (ES) bank codes from ECB.

Source: ECB monthly list of financial institutions
URL:    https://www.ecb.europa.eu/stats/financial_corporations/list_of_financial_institutions/html/monthly_list-MID.en.html
"""

import csv
import io
import json
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "src" / "iban_tools" / "data"


def scrape_fr_es() -> dict[str, dict[str, str]]:
    """Scrape FR and ES bank code → BIC mappings from ECB."""
    base = "https://www.ecb.europa.eu"
    list_url = base + "/stats/financial_corporations/list_of_financial_institutions/html/monthly_list-MID.en.html"

    print("[FR/ES] Fetching ECB list page...")
    page = requests.get(list_url, timeout=30)
    page.raise_for_status()

    soup = BeautifulSoup(page.text, "html.parser")
    main_table = soup.select("main table a")

    csv_url = None
    for link in main_table:
        href = link.get("href", "")
        if href.endswith(".csv"):
            csv_url = base + href
            break

    if not csv_url:
        print("[FR/ES] ERROR: Could not find CSV download link on ECB page.")
        return {"fr": {}, "es": {}}

    print(f"[FR/ES] Downloading CSV from {csv_url}...")
    resp = requests.get(csv_url, timeout=60)
    resp.raise_for_status()

    # Try UTF-16, fallback to UTF-8
    try:
        content = resp.content.decode("utf-16")
    except (UnicodeDecodeError, UnicodeError):
        content = resp.content.decode("utf-8")

    # Parse TSV
    reader = csv.DictReader(io.StringIO(content), delimiter="\t")

    result: dict[str, dict[str, str]] = {"fr": {}, "es": {}}

    for row in reader:
        riad_code = row.get("RIAD_CODE", "").strip()
        bic = row.get("BIC", "").strip()

        if not riad_code or not bic:
            continue

        country = riad_code[:2].lower()
        if country not in ("fr", "es"):
            continue

        bank_code = riad_code[2:]
        result[country][bank_code] = bic

    print(f"[FR] Found {len(result['fr'])} bank codes.")
    print(f"[ES] Found {len(result['es'])} bank codes.")
    return result


def main():
    data = scrape_fr_es()
    for country in ("fr", "es"):
        if data[country]:
            output = DATA_DIR / f"{country}.json"
            with output.open("w", encoding="utf-8") as f:
                json.dump(data[country], f, ensure_ascii=False)
            print(f"[{country.upper()}] Written to {output}")
        else:
            print(f"[{country.upper()}] No data scraped, keeping existing file.", file=sys.stderr)


if __name__ == "__main__":
    main()
