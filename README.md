# FPS Sale Transaction Scraper

A Selenium-based data extraction and transformation pipeline for collecting Fair Price Shop (FPS) sale transaction data from the Integrated Management of Public Distribution System (IMPDS) portal.

The project follows a simple ETL-style workflow:

```text
IMPDS Portal
     ↓
Selenium Navigation
     ↓
FPS-level Extraction
     ↓
Raw JSON
     ↓
Cleaning & Flattening
     ↓
Consolidated CSV
```

The scraper is designed around the structure of the IMPDS sale portal, where selecting an FPS dynamically updates the transaction panel without a traditional full-page navigation.

---

## 1. Objective

The objective of this project is to collect FPS-level transaction information for Goa and transform the nested portal data into an analysis-ready tabular dataset.

The target hierarchy is:

```text
Year + Month
    ↓
State
    ↓
District
    ↓
FPS List
    ↓
Individual FPS
    ↓
Summary + Transaction Tables
```

The project supports the two Goa districts required for the assignment:

- North Goa
- South Goa

The target reporting periods are:

- March 2026
- April 2026

Each FPS/month combination is represented as an individual raw record and can subsequently be represented as one row in the consolidated dataset.

---

## 2. Source

The source is the publicly accessible IMPDS Sale portal:

```text
https://impds.nic.in/sale/
```

The portal dynamically updates the FPS information after an FPS is selected. Selenium is therefore used to reproduce the browser interactions and read the updated DOM.

---

## 3. Data Extracted

### FPS Metadata

Each raw record contains:

| Field | Description |
|---|---|
| `year` | Reporting year |
| `month` | Reporting month |
| `state` | State |
| `district` | District |
| `fps_id` | FPS identifier |
| `fps_name` | FPS name, when available from the portal |

### Summary Statistics

The scraper extracts the summary-card metrics displayed by the portal, including:

- Total e-Transactions
- Aadhaar Authenticated Transactions
- Other Mode Authenticated Transactions
- Non-Authenticated Transactions

### Number of Transactions

The transaction table contains the major ration-card categories, including:

- Priority Household (PHH)
- Antyodaya Anna Yojana (AAY)

Each category is captured across:

- Regular
- Intra State
- Inter State
- Total

### Number of Transacted Ration Cards

The ration-card table is captured using the same transaction dimensions:

- Regular
- Intra State
- Inter State
- Total

### Distributed Quantity

Distributed quantities are captured in kilograms for the commodities exposed by the portal:

- Wheat
- Fortified Rice
- Rice
- Coarse Grains
- Barley
- Bajra
- Maize
- Jowar
- Ragi
- Kodo

For the expanded commodity rows, the following dimensions are retained:

- Regular
- Intra State
- Inter State
- Total

### Coarse Grains

The portal exposes Coarse Grains as a category with individual sub-commodities. The raw data preserves the individual rows rather than collapsing them into a single value:

- Barley
- Bajra
- Maize
- Jowar
- Ragi
- Kodo

This allows the consolidated dataset to analyse each coarse-grain commodity independently.

---

## 4. Scraping Approach

### Dynamic/AJAX content

The FPS information is updated dynamically after an FPS is selected. The navigation layer therefore:

1. Opens the IMPDS sale portal.
2. Opens the reporting-month calendar.
3. Selects the required month.
4. Opens the state selection.
5. Selects Goa.
6. Opens the district selection.
7. Selects North Goa or South Goa.
8. Opens the FPS list.
9. Dynamically discovers the available FPS IDs.
10. Selects each FPS.
11. Waits for the dynamically updated transaction table.
12. Passes the current page to the parser.

The navigation code uses Selenium explicit waits rather than relying exclusively on fixed delays for page navigation.

---

## 5. Parser Design

The parser is separated from browser navigation so that page interaction and data extraction remain independent responsibilities.

`parser.py` provides two main operations:

### `extract_summary_cards()`

Locates the summary-card elements and maps their labels to their displayed values.

### `extract_table(table_name)`

Locates a table by its `aria-label`, iterates through its rows, and extracts:

```text
Regular
Intra State
Inter State
Total
```

The parser ignores the aggregate `Total` row and skips malformed rows that do not contain the expected number of cells.

This keeps the extraction logic reusable across the three portal tables.

---

## 6. Error Handling and Resume Behaviour

FPS-level extraction is isolated inside exception handling. If one FPS fails, the error is logged and processing continues with the remaining FPS records.

Raw files are written immediately after a successful FPS extraction instead of waiting for the entire district to finish.

The scraper also checks whether the expected raw JSON file already exists. Existing records can therefore be skipped when resuming a partially completed run.

Example progress output:

```text
Found 200 FPS in North Goa

[1/200] Processing FPS: 158500100001
✓ Saved successfully

[2/200] Processing FPS: 158500100002
✓ Saved successfully
```

If an individual record fails:

```text
✗ Failed FPS: 158500100010
```

The failure does not terminate the complete district run.

> **Note:** The current implementation uses FPS-level exception handling and resume-by-existing-file behaviour. It does not implement an automatic multi-attempt retry queue.

---

## 7. Raw Data Organization

Raw records are organized by reporting period and district:

```text
FPS-SCRAPER/
└── data/
    └── raw/
        ├── 2026-03/
        │   ├── north_goa/
        │   │   ├── <fps_id>.json
        │   │   └── ...
        │   └── south_goa/
        │       └── ...
        │
        └── 2026-04/
            ├── north_goa/
            │   └── ...
            └── south_goa/
                └── ...
```

Keeping one JSON file per FPS makes individual records easy to inspect, preserves the raw nested structure, and allows a partially completed scraping run to be resumed.

---

## 8. Raw JSON Structure

A raw FPS record follows the general structure:

```json
{
    "year": "2026",
    "month": "March",
    "state": "GOA",
    "district": "NORTH GOA",
    "fps_id": "158500100001",
    "fps_name": "Example FPS",
    "summary_cards": {},
    "number_of_transactions": [],
    "number_of_transacted_ration_cards": [],
    "distributed_quantity_kg": []
}
```

The raw layer retains nested information before transformation so that the original FPS-level structure remains available for auditing or reprocessing.

---

## 9. Data Consolidation

`consolidate_data.py` transforms all raw JSON records under `data/raw/` into a single analysis-ready CSV.

The consolidation process:

1. Recursively discovers JSON files.
2. Loads each FPS record.
3. Extracts metadata.
4. Flattens summary-card values.
5. Flattens the transaction table.
6. Flattens the ration-card table.
7. Flattens distributed quantities.
8. Preserves individual Coarse Grain commodities.
9. Cleans numeric values.
10. Creates basic data-quality flags.
11. Writes the final CSV.

Output:

```text
data/processed/consolidated.csv
```

The intended grain of the consolidated dataset is **one row per FPS per reporting month**.

---

## 10. Transformation Rules

### Numeric cleaning

Scraped numeric fields can contain formatting such as commas or blank strings.

The consolidation step:

- strips commas from numeric text
- converts numeric strings to numeric values
- treats empty numeric fields as zero where appropriate
- preserves values that cannot safely be converted to numeric form

### Column naming

Nested labels are normalized into descriptive snake-case column names.

For example:

```text
Priority Household (PHH)
+
Regular
```

becomes a column similar to:

```text
txn_priority_household_phh_regular
```

A commodity field follows the same pattern:

```text
distribution_rice_regular
distribution_rice_intra_state
distribution_rice_inter_state
distribution_rice_total
```

This produces a flat structure suitable for pandas, SQL databases, Power BI, or other analytical tools.

---

## 11. Data Quality

The consolidation process records basic indicators for the presence of the three main tables:

```text
has_transactions_data
has_ration_cards_data
has_distribution_data
```

It also creates a `no_transactions` indicator.

A zero-transaction FPS is not automatically treated as a scraping failure. It can represent a legitimate reporting-period observation. This distinction allows missing data and genuine zero activity to be analysed separately.

Malformed JSON files are skipped and reported rather than terminating the entire consolidation process.

---

## 12. Repository Structure

```text
FPS-SCRAPER/
│
├── fps_scraper/
│   ├── __init__.py
│   ├── navigator.py
│   └── parser.py
│
├── data/
│   ├── raw/
│   │   ├── 2026-03/
│   │   │   ├── north_goa/
│   │   │   └── south_goa/
│   │   └── 2026-04/
│   │       ├── north_goa/
│   │       └── south_goa/
│   │
│   └── processed/
│       └── consolidated.csv
│
├── sample_output/
│   └── sample_output.json
│
├── get_raw_data.py
├── consolidate_data.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

### Main files

| File | Purpose |
|---|---|
| `fps_scraper/navigator.py` | Selenium browser navigation and dynamic FPS selection |
| `fps_scraper/parser.py` | Extraction of summary cards and transaction tables |
| `get_raw_data.py` | Configured scraping runner and raw JSON writer |
| `consolidate_data.py` | Raw JSON transformation and CSV generation |
| `requirements.txt` | Python dependencies |
| `sample_output/sample_output.json` | Representative raw-output example |
| `.gitignore` | Excludes generated/local files from version control |

---

## 13. Configuration

The reporting period and district are configured near the top of `get_raw_data.py`:

```python
YEAR = "2026"
MONTH = "03"
STATE = "GOA"
DISTRICT = "north_goa"
```

The navigation layer supports:

```text
north_goa
south_goa
```

To run another reporting period or district, update the configuration before starting the scraper.

---

## 14. Installation

Clone the repository:

```bash
git clone https://github.com/sxkshmgit/FPS-SCRAPER.git
cd FPS-SCRAPER
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

The project uses Selenium with Chrome WebDriver. `webdriver-manager` is used to manage the Chrome driver installation.

---

## 15. Running the Scraper

Configure the required period and district in `get_raw_data.py`, then run:

```bash
python get_raw_data.py
```

Successful records are written below:

```text
data/raw/<year>-<month>/<district>/
```

For example:

```text
data/raw/2026-03/north_goa/158500100001.json
```

---

## 16. Running Consolidation

After raw JSON files have been collected, run:

```bash
python consolidate_data.py
```

The output is written to:

```text
data/processed/consolidated.csv
```

The consolidation step can be rerun without scraping the portal again, because it operates on the stored raw JSON layer.

---

## 17. Sample Output

`sample_output/sample_output.json` provides a representative example of the raw FPS-level structure.

It demonstrates the presence of:

- FPS metadata
- Summary metrics
- PHH/AAY transaction data
- Transacted ration-card data
- Distributed quantities
- Expanded Coarse Grain commodities

This allows the output schema to be inspected without running Selenium.

---

## 18. Engineering Decisions

### Why Selenium?

The portal is interactive and dynamically updates FPS information after a user selects an FPS. Selenium provides browser-level interaction and access to the updated DOM.

### Why separate navigation and parsing?

`Navigator` is responsible for interacting with the website, while `Parser` is responsible for extracting structured values. Separating these responsibilities makes the code easier to understand and maintain.

### Why save one FPS per JSON file?

Saving records independently reduces the impact of individual scraping failures and makes partial runs resumable. It also preserves a traceable raw record for each FPS.

### Why separate raw and processed layers?

The raw layer preserves the scraped structure, while the processed layer is optimized for analysis. This separation allows transformations to be rerun without repeatedly hitting the source portal.

---

## 19. Assumptions

1. The IMPDS portal is accessible during a scraping run.
2. The relevant tables retain the expected HTML structure and `aria-label` values.
3. FPS IDs can be used as identifiers for individual FPS records.
4. A zero transaction count can be a legitimate observation.
5. Raw records are retained before flattening so transformations can be reproduced.

---

## 20. Known Limitations

- The scraper depends on the current HTML structure and selectors of the IMPDS portal.
- Network or portal responsiveness can cause individual FPS extraction failures.
- Failed FPS records are logged and skipped; the current implementation does not maintain a separate retry queue.
- The current runner requires the reporting period and district to be configured manually.
- Selenium requires a compatible browser environment.
- Large raw datasets may be excluded from Git version control to keep the repository lightweight.

---

## 21. Future Improvements

Potential improvements include:

- Automatic iteration across all required month/district combinations
- Dedicated retry queues for failed FPS records
- Structured logging to a log file
- Automated schema validation
- Unit tests for transformation functions
- PostgreSQL loading
- Apache Airflow orchestration
- Dockerization
- Cloud execution
- Automated data-quality reporting

---

## 22. Assignment Coverage

| Requirement | Implementation |
|---|---|
| Navigate month/year | Selenium navigation |
| Navigate Goa | Selenium navigation |
| North Goa | District navigation support |
| South Goa | District navigation support |
| FPS discovery | Dynamic FPS ID collection |
| Summary cards | `Parser.extract_summary_cards()` |
| Number of Transaction | `Parser.extract_table()` |
| Transacted Ration Card | `Parser.extract_table()` |
| Distributed Quantity | `Parser.extract_table()` |
| Coarse Grain sub-commodities | Preserved as individual commodity rows |
| Dynamic/AJAX handling | Explicit Selenium waits for updated content |
| Error handling | FPS-level exception handling |
| Progress logging | Console progress output |
| Partial-run recovery | Existing raw files are skipped |
| Raw data | FPS-level JSON |
| Consolidation | `consolidate_data.py` |
| Numeric cleaning | Consolidation step |
| Analysis-ready dataset | `data/processed/consolidated.csv` |

---

## 23. License

This project is released under the MIT License.

See [`LICENSE`](LICENSE) for details.
