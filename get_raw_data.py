#Adding Imports
from scraper.navigator import Navigator
from scraper.parser import Parser

import json
import time
import traceback


# Initialize the browser navigation and page parsing components.
navigator = Navigator()
parser = Parser(navigator.driver)


# Navigate to the PDS portal and select the required month, state,
# and district before loading the FPS list.
navigator.open_site()

navigator.open_calendar()
navigator.select_month("mar")

navigator.open_states()
navigator.select_state("30")

navigator.open_districts()
navigator.select_district("north_goa")

navigator.open_fps_list()


# Collect all FPS IDs available for the selected district and month.
fps_ids = navigator.get_all_fps_ids()

print(f"Found {len(fps_ids)} FPS")


# Store the scraped records before exporting them to JSON.
all_fps_data = []


# Process each FPS independently so that a failed FPS does not
# terminate the entire scraping run.
for index, fps_id in enumerate(fps_ids, start=1):

    print(f"\n[{index}/{len(fps_ids)}] Processing FPS: {fps_id}")

    try:

        # Open the selected FPS and wait for its dynamic data to load.
        navigator.click_fps(fps_id)

        # Allow the AJAX-driven panel to finish updating before parsing.
        time.sleep(3)

        # Extract the four summary card values.
        summary = parser.extract_summary_cards()

        # Extract the three transaction-related tables.
        transactions = parser.extract_table(
            "Number of Transaction"
        )

        ration_cards = parser.extract_table(
            "Number of Transacted Ration Card"
        )

        distribution = parser.extract_table(
            "Distributed Quantity(In Kg)"
        )

        # Combine all extracted information into a single FPS record.
        fps_data = {
            "fps_id": fps_id,
            "summary": summary,
            "transactions": transactions,
            "ration_cards": ration_cards,
            "distribution": distribution
        }

        all_fps_data.append(fps_data)

        print("✓ Scraped successfully")

    except Exception:

        # Log the error and continue with the remaining FPS records.
        print(f"\n✗ Failed FPS: {fps_id}")
        traceback.print_exc()

        continue


# Export all successfully scraped FPS records as structured JSON.
with open("output.json", "w", encoding="utf-8") as file:
    json.dump(
        all_fps_data,
        file,
        indent=4,
        ensure_ascii=False
    )

print(f"\nSaved {len(all_fps_data)} FPS records to output.json")


# Keep the browser open until the user confirms that the run is complete.
input("Press Enter to close the browser...")

navigator.close()
