from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os

class RealEstateScraper:
    """A class to scrape real estate data from cenenekretnina.rs."""
    
    def __init__(self, logger, headless=False):
        """Initialize the scraper with a logger and headless option."""
        self.logger = logger
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless=new')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def initialize_driver(self):
        """Set up the Chrome WebDriver."""
        try:
            self.logger.log("Initializing Chrome driver...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            self.driver.implicitly_wait(10)
            self.logger.log("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.log(f"Failed to initialize Chrome driver: {str(e)}", "error")
            raise

    def wait_for_element(self, by, value, timeout=20, clickable=False):
        """Wait for an element to be present or clickable."""
        try:
            self.logger.log(f"Waiting for element: {value}")
            wait = WebDriverWait(self.driver, timeout)
            condition = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
            element = wait.until(condition((by, value)))
            self.logger.log(f"Element found: {value}")
            return element
        except TimeoutException:
            self.logger.log(f"Timeout waiting for element: {value}", "error")
            raise
        except Exception as e:
            self.logger.log(f"Error finding element {value}: {str(e)}", "error")
            raise

    def safe_click(self, element, wait_time=1):
        """Safely click an element with scrolling and delay."""
        try:
            self.logger.log("Attempting to click element")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(wait_time)
            element.click()
            time.sleep(wait_time)
            self.logger.log("Element clicked successfully")
        except Exception as e:
            self.logger.log(f"Failed to click element: {str(e)}", "error")
            raise

    def set_filters(self, view_type, period, year, region, sub_region=None):
        """Apply filters on the website."""
        try:
            self.logger.log(f"Setting filters - View Type: {view_type}, Period: {period}, Year: {year}, Region: {region}")
            self.driver.get("https://www.cenenekretnina.rs/")
            time.sleep(5)
            
            first_button = self.wait_for_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div/div/button[4]", clickable=True)
            self.safe_click(first_button)
            second_button = self.wait_for_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div[2]", clickable=True)
            self.safe_click(second_button)

            # View type selection
            self.logger.log(f"Selecting view type: {view_type}")
            view_xpath = "//button[contains(text(), 'Mesečno')]" if view_type == "monthly" else "//button[contains(text(), 'Kvartalno')]"
            view_button = self.wait_for_element(By.XPATH, view_xpath, clickable=True)
            self.safe_click(view_button)

            # Period selection
            self.logger.log(f"Selecting period: {period}")
            period_dropdown = self.wait_for_element(By.XPATH, "//div[contains(@class, 'MuiSelect-select')]", clickable=True)
            self.safe_click(period_dropdown)
            period_option = self.wait_for_element(By.XPATH, f"//li[contains(@class, 'MuiMenuItem-root') and text()='{period}']", clickable=True)
            self.safe_click(period_option)

            # Year selection
            self.logger.log(f"Selecting year: {year}")
            year_dropdown = self.wait_for_element(By.XPATH, "(//div[contains(@class, 'MuiSelect-select')])[2]", clickable=True)
            self.safe_click(year_dropdown)
            year_option = self.wait_for_element(By.XPATH, f"//li[contains(@class, 'MuiMenuItem-root') and text()='{year}']", clickable=True)
            self.safe_click(year_option)

            # Region selection
            if region:
                self.logger.log(f"Selecting region: {region}")
                region_dropdown = self.wait_for_element(By.XPATH, "(//div[contains(@class, 'MuiSelect-select')])[3]", clickable=True)
                self.safe_click(region_dropdown)
                region_option = self.wait_for_element(By.XPATH, f"//li[contains(@class, 'MuiMenuItem-root') and text()='{region}']", clickable=True)
                self.safe_click(region_option)

            # Sub-region selection
            if sub_region and sub_region != "Sve":
                self.logger.log(f"Selecting sub-region: {sub_region}")
                sub_region_dropdown = self.wait_for_element(By.XPATH, "(//div[contains(@class, 'MuiSelect-select')])[4]", clickable=True)
                self.safe_click(sub_region_dropdown)
                sub_region_option = self.wait_for_element(By.XPATH, f"//li[contains(@class, 'MuiMenuItem-root') and text()='{sub_region}']", clickable=True)
                self.safe_click(sub_region_option)

            # Apply filters
            search_button = self.wait_for_element(By.XPATH, "//button[contains(text(), 'Primeni')]", clickable=True)
            self.safe_click(search_button, wait_time=2)
            self.logger.log("Filters applied successfully")

        except Exception as e:
            self.logger.log(f"Error in set_filters: {str(e)}", "error")
            raise

    def scrape_data(self):
        """Scrape data from the website."""
        all_data = []
        page = 1
        total_rows = 0
        
        try:
            self.logger.log("Starting data scraping...")
            time.sleep(2)
            pagination_text = self.driver.find_element(By.CLASS_NAME, "MuiTablePagination-displayedRows").text
            total_items = int(pagination_text.split(" ")[-1])
            items_per_page = 25
            total_pages = (total_items + items_per_page - 1) // items_per_page
            
            self.logger.log(f"Found {total_items} items across {total_pages} pages")
            
            while True:
                start_time = time.time()
                self.wait_for_element(By.CLASS_NAME, "MuiDataGrid-row")
                rows = self.driver.find_elements(By.CLASS_NAME, "MuiDataGrid-row")
                self.logger.log(f"Processing page {page}/{total_pages} with {len(rows)} rows")
                
                for row_index, row in enumerate(rows, 1):
                    try:
                        cells = row.find_elements(By.CLASS_NAME, "MuiDataGrid-cell")
                        if len(cells) >= 7:
                            predmet_cell = cells[5]
                            predmet_labels = [label.get_attribute('aria-label') 
                                            for label in predmet_cell.find_elements(By.CSS_SELECTOR, '[aria-label]')]
                            predmet_text = ', '.join(predmet_labels)
                            
                            data = {
                                'Tip': cells[0].text,
                                'Datum': cells[1].text,
                                'Cena': cells[2].text,
                                'Površina': cells[3].text,
                                'Cena/m²': cells[4].text,
                                'Predmet': predmet_text,
                                'Lokacija': cells[6].text
                            }
                            all_data.append(data)
                            total_rows += 1
                            
                            if row_index % 5 == 0:
                                self.logger.log(f"Processed {row_index}/{len(rows)} rows on page {page}")
                                
                    except Exception as e:
                        self.logger.log(f"Error processing row {row_index} on page {page}: {str(e)}", "error")
                        continue
                
                page_time = time.time() - start_time
                self.logger.log(f"Page {page} completed in {page_time:.2f} seconds")
                
                try:
                    next_button = self.wait_for_element(By.XPATH, "//button[@aria-label='Sledeća strana']", timeout=5)
                    if 'Mui-disabled' in next_button.get_attribute('class'):
                        self.logger.log("Reached last page")
                        break
                    self.safe_click(next_button)
                    page += 1
                    self.logger.log(f"Moving to page {page}")
                except Exception:
                    self.logger.log("No more pages to scrape")
                    break
                    
            self.logger.log(f"Scraping completed. Total rows scraped: {total_rows}")
            return all_data
            
        except Exception as e:
            self.logger.log(f"Error during scraping: {str(e)}", "error")
            raise

    def save_to_excel(self, data, filename='real_estate_data.xlsx'):
        """Save scraped data to an Excel file."""
        try:
            if not data:
                self.logger.log("No data to save", "warning")
                return
            self.logger.log(f"Saving {len(data)} records to Excel file: {filename}")
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            self.logger.log("Data saved successfully")
        except Exception as e:
            self.logger.log(f"Error saving to Excel: {str(e)}", "error")
            raise

    def close(self):
        """Close the WebDriver."""
        if hasattr(self, 'driver'):
            try:
                self.logger.log("Closing browser")
                self.driver.quit()
                self.logger.log("Browser closed successfully")
            except Exception as e:
                self.logger.log(f"Error closing browser: {str(e)}", "error")
