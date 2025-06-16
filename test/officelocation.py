import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options


def fill_officeloc_forms(driver):
    options = Options()
    options.add_experimental_option("detach", True)  

    df = pd.read_excel(r"off.xlsx")  

    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Office Location')]")
    button.click()

    # Loop through the rows in the dataframe
    for index, row in df.iterrows():
        print(list(df.columns))  # Check exact column names

        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]").click()
        time.sleep(1)

        # Fill in the form fields
        driver.find_element(By.NAME, "location").send_keys(row["location"])
        driver.find_element(By.NAME, "contact").send_keys(row["contact"])
        # driver.find_element(By.NAME, "gst_no").send_keys(row["gst_no"])

        try:
            # Country field
            country_name = row["country"]  
            autocomplete_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "country-select"))
            )
            autocomplete_input.clear()
            autocomplete_input.send_keys(country_name[:10]) 
            time.sleep(1)

            dropdown_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
            )

            available_countries = [opt.text.strip() for opt in dropdown_options]
            print("Dropdown options:", available_countries)

            for option in dropdown_options:
                if option.text.strip().endswith(country_name):  # Match exact country
                    ActionChains(driver).move_to_element(option).click().perform()
                    time.sleep(1)
                    break
                else:
                    print(f"Country '{country_name}' not found in dropdown!")

            # State field
            state_name = row["state"]  # Take state from Excel
            autocomplete_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "state-select"))
            )
            autocomplete_input.clear()
            autocomplete_input.send_keys(state_name[:10])
            time.sleep(1) 

            dropdown_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
            )

            available_states = [opt.text.strip() for opt in dropdown_options]
            print("Dropdown options:", available_states)

            for option in dropdown_options:
                if option.text.strip().endswith(state_name):  
                    ActionChains(driver).move_to_element(option).click().perform()
                    time.sleep(1)
                    break
            else:
                print(f"State '{state_name}' not found in dropdown!")

            # City field
            city_name = row["city"]  # Take state from Excel
            autocomplete_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "city-select"))
            )
            autocomplete_input.clear()
            autocomplete_input.send_keys(city_name[:10])
            time.sleep(1) 

            dropdown_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
            )

            available_states = [opt.text.strip() for opt in dropdown_options]
            print("Dropdown options:", available_states)

            for option in dropdown_options:
                if option.text.strip().endswith(city_name):  
                    ActionChains(driver).move_to_element(option).click().perform()
                    time.sleep(1)
                    break
            else:
                print(f"State '{city_name}' not found in dropdown!")


        except Exception as e:
            print(f"Error: {e}")

        # Fill in remaining form fields
        # driver.find_element(By.NAME, "pincode").send_keys(row["pincode"])
        driver.find_element(By.NAME, "address").send_keys(row["address"])

        button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
        )
        button.click()
        time.sleep(2)

# # Wait for a few seconds before quitting
# time.sleep(15)
# driver.quit()
# print("Done")
