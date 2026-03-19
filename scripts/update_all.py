#!/usr/bin/env python3
"""Master script: update all BIC datasets by running all scrapers.

Usage:
    python scripts/update_all.py          # Run all scrapers
    python scripts/update_all.py de at    # Run specific country scrapers only
"""

import sys
import time
from pathlib import Path

# Add project root to path so scrapers can find the data dir
sys.path.insert(0, str(Path(__file__).parent))

from scrape_at import scrape_at, main as at_main  # noqa: E402
from scrape_be import scrape_be, main as be_main  # noqa: E402
from scrape_de import scrape_de, main as de_main  # noqa: E402
from scrape_fr_es import scrape_fr_es, main as fr_es_main  # noqa: E402
from scrape_lu import scrape_lu, main as lu_main  # noqa: E402
from scrape_nl import scrape_nl, main as nl_main  # noqa: E402

SCRAPERS: dict[str, callable] = {
    "de": de_main,
    "at": at_main,
    "be": be_main,
    "nl": nl_main,
    "fr": fr_es_main,
    "es": fr_es_main,  # FR/ES share a single scraper
    "lu": lu_main,
}


def main():
    requested = [a.lower() for a in sys.argv[1:]] if len(sys.argv) > 1 else list(SCRAPERS.keys())

    # FR and ES share a scraper, deduplicate
    if "fr" in requested and "es" in requested:
        requested = [c for c in requested if c != "es"]

    print("=" * 60)
    print("IBAN Tools — BIC Data Update")
    print("=" * 60)
    print(f"Countries: {', '.join(c.upper() for c in requested)}")
    print()

    success = []
    failed = []
    start = time.time()

    for country in requested:
        scraper = SCRAPERS.get(country)
        if not scraper:
            print(f"[WARN] Unknown country: {country}, skipping.")
            continue

        try:
            print(f"--- {country.upper()} ---")
            scraper()
            success.append(country.upper())
        except Exception as e:
            print(f"[ERROR] {country.upper()} scraper failed: {e}")
            failed.append(country.upper())

        print()

    elapsed = time.time() - start
    print("=" * 60)
    print(f"Done in {elapsed:.1f}s")
    print(f"  Success: {', '.join(success) if success else 'none'}")
    if failed:
        print(f"  Failed:  {', '.join(failed)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
