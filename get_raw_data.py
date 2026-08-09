from scraper.navigator import Navigator
from scraper.parser import Parser

import json
import time
import traceback
from pathlib import Path


# Initialize the browser navigator and page parser.
navigator = Navigator()
parser = Parser(navigator.driver)


# Select the reporting period, state, and district to scrape.
YEAR = "2026"
MONTH = "03"
STATE = "GOA"
DISTRICT = "north_goa"


# Create the raw-data directory for the selected month and district.
output_dir = Path(
    f"data/raw/{YEAR}-{MONTH}/{DISTRICT}"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True
)


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

print(
    f"Found {len(fps_ids)} FPS in "
    f"{DISTRICT.replace('_', ' ').title()}"
)


# Process each FPS independently so completed records can be
# retained even if another FPS fails during the run.
for index, fps_id in enumerate(fps_ids, start=1):

    output_file = output_dir / f"{fps_id}.json"

    print(
        f"\n[{index}/{len(fps_ids)}] "
        f"Processing FPS: {fps_id}"
    )

    # Skip FPS records that were already successfully saved.
    if output_file.exists():

        print("Already scraped — skipping.")

        continue

    try:

        # Open the selected FPS and wait for its AJAX-loaded data.
        navigator.click_fps(fps_id)

        time.sleep(3)

        # Extract the summary cards and three available tables.
        summary = parser.extract_summary_cards()

        transactions = parser.extract_table(
            "Number of Transaction"
        )

        ration_cards = parser.extract_table(
            "Number of Transacted Ration Card"
        )

        distribution = parser.extract_table(
            "Distributed Quantity(In Kg)"
        )

        # Store all information associated with the FPS.
        fps_data = {
            "year": YEAR,
            "month": MONTH,
            "state": STATE,
            "district": DISTRICT,
            "fps_id": fps_id,
            "summary": summary,
            "transactions": transactions,
            "ration_cards": ration_cards,
            "distribution": distribution
        }

        # Save the FPS immediately instead of waiting until the
        # entire district has been scraped.
        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                fps_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("✓ Saved successfully")

    except Exception:

        # Log the failed FPS and continue with the remaining records.
        print(f"\n✗ Failed FPS: {fps_id}")

        traceback.print_exc()

        continue


print(
    f"\nScraping completed for "
    f"{DISTRICT.replace('_', ' ').title()}."
)

input("Press Enter to close the browser...")

navigator.close()
