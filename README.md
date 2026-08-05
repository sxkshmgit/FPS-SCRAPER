# FPS Sale Transaction Scraper

A robust Python-based data extraction pipeline that automates the collection of Fair Price Shop (FPS) sale transaction data from the Integrated Management of Public Distribution System (IMPDS) portal.

The project scrapes transaction data for every Fair Price Shop (FPS) in Goa across multiple months, transforms the extracted data into a structured format, and consolidates it into an analysis-ready dataset.

---

## Features

### Automated Navigation

- Select transaction month and year
- Navigate to Goa state
- Navigate through North Goa and South Goa districts
- Automatically retrieve every FPS available
- Dynamically iterate through all FPS without hardcoded IDs

### Data Extraction

For every FPS, the scraper extracts:

#### Summary Statistics

- Total e-Transactions
- Aadhaar Authenticated Transactions
- Other Mode Authenticated Transactions
- Non-Authenticated Transactions

#### Number of Transactions

- Priority Household (PHH)
- Antyodaya Anna Yojana (AAY)

Including:

- Regular
- Intra State
- Inter State
- Total

#### Number of Transacted Ration Cards

Including:

- Regular
- Intra State
- Inter State
- Total

#### Distributed Quantity

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

Including:

- Regular
- Intra State
- Inter State
- Total

---

## Data Pipeline

```
IMPDS Portal
        │
        ▼
 Selenium Automation
        │
        ▼
 Raw FPS-Level JSON
        │
        ▼
 Data Cleaning
        │
        ▼
 Consolidation
        │
        ▼
 Analysis Ready CSV
```

---

## Project Structure

```
fps_scraper/
│
├── scraper/
│   ├── navigator.py
│   ├── parser.py
│   └── saver.py
│
├── data/
│   ├── raw/
│   │   ├── 2026-03/
│   │   └── 2026-04/
│   │
│   └── processed/
│       └── consolidated.csv
│
├── get_raw_data.py
├── consolidate_data.py
├── requirements.txt
└── README.md
```

---

## Technologies Used

- Python
- Selenium
- WebDriver Manager
- JSON
- CSV
- Pandas

---

## Key Features

- Dynamic Selenium navigation
- AJAX content handling
- Generic HTML table parser
- Modular architecture
- Retry and exception handling
- Progress logging
- Automatic JSON generation
- Dataset consolidation
- Clean, reusable codebase

---

## Output

### Raw Data

Each FPS is stored individually as JSON.

Example:

```
data/raw/2026-03/north_goa/158500100001.json
```

### Processed Data

A consolidated CSV containing one row per FPS per month with flattened transaction metrics.

Example:

```
data/processed/consolidated.csv
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/your-username/fps_scraper.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the scraper

```bash
python get_raw_data.py
```

Generate the consolidated dataset

```bash
python consolidate_data.py
```

---

## Engineering Highlights

- Designed using a modular architecture separating navigation, parsing, and data processing.
- Generic HTML table parser capable of extracting multiple table layouts.
- Dynamic FPS discovery without hardcoded shop IDs.
- Handles asynchronous page updates using Selenium waits.
- Produces structured datasets suitable for downstream analytics and visualization.

---

## Future Enhancements

- PostgreSQL data loading
- Docker containerization
- Apache Airflow scheduling
- Power BI dashboard
- Cloud deployment
- Automated testing

---

## License

This project is intended for educational and data engineering portfolio purposes using publicly accessible data.
