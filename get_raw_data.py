"""Run the FPS scraper for a configured reporting period and district."""

import json
import traceback
from pathlib import Path

from fps_scraper.navigator import Navigator
from fps_scraper.parser import Parser


# Configure the reporting period and district to scrape.
YEAR = "2026"
MONTH = "03"
STATE = "GOA"
DISTRICT = "north_goa"


# Initialize the browser navigator and page parser.
navigator = Navigator()
parser = Parser(navigator.driver)


# Create the raw-data directory for the selected month and district.
output_dir = Path(f"data/raw/{YEAR}-{MONTH}/{DISTRICT}")
output_dir.mkdir(parents=True, exist_ok=True)


try:
    # Navigate to the selected month, state, and district.
    navigator.open_site()
    navigator.open_calendar()
    navigator.select_month("mar")
    navigator.open_states()
    navigator.select_state("30")
    navigator.open_districts()
    navigator.select_district(DISTRICT)
    navigator.open_fps_list()

    # Collect all FPS IDs available for the selected district.
    fps_ids = navigator.get_all_fps_ids()
    print(f"Found {len(fps_ids)} FPS in {DISTRICT.replace('_', ' ').title()}")

    # Process each FPS independently so completed records are retained
    # even if another FPS fails during the run.
    for index, fps_id in enumerate(fps_ids, start=1):
        output_file = output_dir / f"{fps_id}.json"

        print(f"\n[{index}/{len(fps_ids)}] Processing FPS: {fps_id}")

        # Skip records that were already successfully saved.
        if output_file.exists():
            print("Already scraped — skipping.")
            continue

        try:
            # Select the FPS and wait for its dynamically updated data.
            navigator.click_fps(fps_id)

            # Extract the summary cards and three transaction tables.
            summary = parser.extract_summary_cards()
            transactions = parser.extract_table("Number of Transaction")
            ration_cards = parser.extract_table("Number of Transacted Ration Card")
            distribution = parser.extract_table("Distributed Quantity(In Kg)")

            fps_data = {
                "year": YEAR,
                "month": MONTH,
                "state": STATE,
                "district": DISTRICT,
                "fps_id": fps_id,
                "summary": summary,
                "transactions": transactions,
                "ration_cards": ration_cards,
                "distribution": distribution,
            }

            # Save each FPS immediately so a partial run can be resumed.
            with output_file.open("w", encoding="utf-8") as file:
                json.dump(fps_data, file, indent=4, ensure_ascii=False)

            print("✓ Saved successfully")

        except Exception:
            # Log the failed FPS and continue with the remaining records.
            print(f"\n✗ Failed FPS: {fps_id}")
            traceback.print_exc()
            continue

    print(f"\nScraping completed for {DISTRICT.replace('_', ' ').title()}.")

finally:
    # Always close the browser when the run finishes.
    navigator.close()
