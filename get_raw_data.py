# Adding Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Navigator:

    # Initialize the Selenium WebDriver and explicit wait used by the scraper.
    def __init__(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 20)

    # Open the IMPDS portal.
    def open_site(self):
        self.driver.get("https://impds.nic.in/sale/")

    # Open the calendar to select the reporting month.
    def open_calendar(self):
        calendar_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[data-bs-target="#myModal10"]')
            )
        )

        calendar_link.click()

    # Select the required reporting month.
    def select_month(self, month):
        month_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'a[key="{month}"]')
            )
        )

        month_link.click()

    # Open the state selection panel.
    def open_states(self):
        states_link = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[data-bs-target="#myModal11"]')
            )
        )

        states_link.click()

    # Select a state using its website-specific state ID.
    def select_state(self, state):
        state_select = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    f'a[onclick="stateData(\'{state}\')"]'
                )
            )
        )

        state_select.click()

    # Open the district selection panel for the selected state.
    def open_districts(self):
        district_link = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'a[onclick="liveDistrictdata(\'30\')"]'
                )
            )
        )

        district_link.click()

    # Select a district using its website-specific district ID.
    def select_district(self, district):
        district_ids = {
            "north_goa": "585",
            "south_goa": "586"
        }

        district_id = district_ids[district]

        district_link = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    f'a[onclick="stateData(\'{district_id}\')"]'
                )
            )
        )

        district_link.click()

    # Open the FPS list for the selected district.
    def open_fps_list(self):
        fps_list_link = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'a[onclick="liveFpsdata(\'30\',\'585\')"]'
                )
            )
        )

        fps_list_link.click()

    # Extract all FPS IDs currently displayed in the FPS list.
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
                fps_id = onclick.split("'")[1]
                fps_ids.append(fps_id)

        return fps_ids

    # Open an individual FPS and wait for its AJAX-loaded data panel.
    def click_fps(self, fps_id):
        selector = f'a[onclick*="{fps_id}"]'

        fps = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    selector
                )
            )
        )

        self.driver.execute_script(
            "arguments[0].click();",
            fps
        )

        self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'table[aria-label="Number of Transaction"] tbody tr'
                )
            )
        )

    # Close the browser and terminate the Selenium session.
    def close(self):
        self.driver.quit()
