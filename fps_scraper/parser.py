from selenium.webdriver.common.by import By


class Parser:

    # Initialize the parser with the active Selenium WebDriver.
    def __init__(self, driver):
        self.driver = driver

    # Extract all rows from a table and organize the values by commodity/category.
    def extract_table(self, table_name):

        table = self.driver.find_element(
            By.CSS_SELECTOR,
            f'table[aria-label="{table_name}"]'
        )

        tbody = table.find_element(
            By.TAG_NAME,
            "tbody"
        )

        rows = tbody.find_elements(
            By.TAG_NAME,
            "tr"
        )

        table_data = {}

        for row in rows:

            cells = row.find_elements(
                By.TAG_NAME,
                "td"
            )

            if len(cells) < 5:
                continue

            row_name = cells[0].text.strip()

            if not row_name or row_name == "Total":
                continue

            table_data[row_name] = {
                "Regular": cells[1].text.strip(),
                "Intra State": cells[2].text.strip(),
                "Inter State": cells[3].text.strip(),
                "Total": cells[4].text.strip()
            }

        return table_data

    # Extract the summary card labels and their corresponding values.
    def extract_summary_cards(self):

        cards = self.driver.find_elements(
            By.CSS_SELECTOR,
            "div.metro-nav-block1"
        )

        summary = {}

        for card in cards:

            try:
                label = card.find_element(
                    By.CSS_SELECTOR,
                    "div.status1"
                ).text.strip()

                value = card.find_element(
                    By.CSS_SELECTOR,
                    "span.counter"
                ).text.strip()

                if label:
                    summary[label] = value

            except Exception:
                continue

        return summary
