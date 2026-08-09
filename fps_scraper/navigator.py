"""Browser navigation helpers for the IMPDS FPS sale portal."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class Navigator:
    """Handle Selenium navigation through the IMPDS portal hierarchy."""

    # Initialize Chrome and the explicit wait used throughout navigation.
    def __init__(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 20)

    # Open the IMPDS sale portal.
    def open_site(self):
        self.driver.get("https://impds.nic.in/sale/")

    # Open the month-selection calendar on the portal.
    def open_calendar(self):
        calendar_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[data-bs-target="#myModal10"]')
            )
        )
        calendar_link.click()

    # Select a reporting month from the calendar.
    def select_month(self, month):
        month_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'a[key="{month}"]')
            )
        )
        month_link.click()

    # Open the state-selection panel.
    def open_states(self):
        states_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[data-bs-target="#myModal11"]')
            )
        )
        states_link.click()

    # Select a state using its portal state identifier.
    def select_state(self, state):
        state_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'a[onclick="stateData(\'{state}\')"]')
            )
        )
        state_link.click()

    # Open the district-selection panel for Goa.
    def open_districts(self):
        district_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[onclick="liveDistrictdata(\'30\')"]')
            )
        )
        district_link.click()

    # Select North Goa or South Goa using the portal district ID.
    def select_district(self, district):
        district_ids = {
            "north_goa": "585",
            "south_goa": "586",
        }

        district_id = district_ids[district]
        district_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'a[onclick="stateData(\'{district_id}\')"]')
            )
        )
        district_link.click()

    # Open the FPS list for the selected Goa district.
    def open_fps_list(self):
        fps_list_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[onclick="liveFpsdata(\'30\',\'585\')"]')
            )
        )
        fps_list_link.click()

    # Read all FPS IDs currently available in the FPS navigation list.
    def get_all_fps_ids(self):
        fps_links = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.menu_list a")
            )
        )

        fps_ids = []

        for fps in fps_links:
            onclick = fps.get_attribute("onclick")
            if onclick:
                fps_ids.append(onclick.split("'")[1])

        return fps_ids

    # Select an FPS and wait until its dynamically updated transaction table appears.
    def click_fps(self, fps_id):
        selector = f'a[onclick*="{fps_id}"]'
        fps = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )

        self.driver.execute_script("arguments[0].click();", fps)

        self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'table[aria-label="Number of Transaction"] tbody tr',
                )
            )
        )

    # Expand the Coarse Grains section so its individual commodities are visible.
    def expand_coarse_grains(self):
        button = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'button.menu-toggle[aria-controls="coarseGrainsPanel"]',
                )
            )
        )

        self.driver.execute_script("arguments[0].click();", button)

        self.wait.until(
            lambda driver: len(
                driver.find_elements(By.CSS_SELECTOR, "tr.customRow")
            ) >= 6
        )

    # Close the browser and end the Selenium session.
    def close(self):
        self.driver.quit()
