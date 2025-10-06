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
from selenium.common.exceptions import TimeoutException


def clear_and_fill_autocomplete(driver, field_id, value):
    """
    Clear previous value from a Material-UI autocomplete and select a new value.
    """
    try:
        input_field = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, field_id))
        )
        input_field.click()
        input_field.send_keys(Keys.CONTROL + "a")  # Select all
        input_field.send_keys(Keys.DELETE)         # Delete
        time.sleep(0.5)

        input_field.send_keys(value[:10])
        time.sleep(1)

        options = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class,'MuiAutocomplete-option')]"))
        )

        for option in options:
            if option.text.strip().endswith(value):
                ActionChains(driver).move_to_element(option).click().perform()
                time.sleep(1)
                break
        else:
            print(f"Value '{value}' not found in {field_id} dropdown!")

    except Exception as e:
        print(f"Error in {field_id}: {e}")


def fill_branch_forms(driver):
    options = Options()
    options.add_experimental_option("detach", True)  

    df = pd.read_excel(r"branch10.xlsx")  

    try:
        tab = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Branch Details']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Branch Details tab not found!")

    # Loop through the rows in the dataframe
    for index, row in df.iterrows():
        print(list(df.columns))  # Check exact column names

        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]").click()
        time.sleep(1)

        # Fill in the form fields
        # driver.find_element(By.NAME, "branch_name").send_keys(row["branch_name"])
        # driver.find_element(By.NAME, "contact").send_keys(row["contact"])
        # driver.find_element(By.NAME, "gst_no").send_keys(row["gst_no"])

        # try:
        #     # Country field
        #     country_name = row["country"]  
        #     autocomplete_input = WebDriverWait(driver, 5).until(
        #         EC.presence_of_element_located((By.ID, "country-select"))
        #     )
        #     autocomplete_input.clear()
        #     autocomplete_input.send_keys(country_name[:10]) 
        #     time.sleep(2)

        #     dropdown_options = WebDriverWait(driver, 5).until(
        #         EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
        #     )

        #     available_countries = [opt.text.strip() for opt in dropdown_options]
        #     print("Dropdown options:", available_countries)

        #     for option in dropdown_options:
        #         if option.text.strip().endswith(country_name):  # Match exact country
        #             ActionChains(driver).move_to_element(option).click().perform()
        #             time.sleep(2)
        #             break
        #         else:
        #             print(f"Country '{country_name}' not found in dropdown!")

        #     # State field
        #     state_name = row["state"]  # Take state from Excel
        #     autocomplete_input = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.ID, "state-select"))
        #     )
        #     autocomplete_input.clear()
        #     autocomplete_input.send_keys(state_name[:10])
        #     time.sleep(2) 

        #     dropdown_options = WebDriverWait(driver, 5).until(
        #         EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
        #     )

        #     available_states = [opt.text.strip() for opt in dropdown_options]
        #     print("Dropdown options:", available_states)

        #     for option in dropdown_options:
        #         if option.text.strip().endswith(state_name):  
        #             ActionChains(driver).move_to_element(option).click().perform()
        #             time.sleep(2)
        #             break
        #     else:
        #         print(f"State '{state_name}' not found in dropdown!")

        #     # City field
        #     city_name = row["city"]  # Take state from Excel
        #     autocomplete_input = WebDriverWait(driver, 5).until(
        #         EC.element_to_be_clickable((By.ID, "city-select"))
        #     )
        #     autocomplete_input.clear()
        #     autocomplete_input.send_keys(city_name[:10])
        #     time.sleep(2) 

        #     dropdown_options = WebDriverWait(driver, 5).until(
        #         EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
        #     )

        #     available_states = [opt.text.strip() for opt in dropdown_options]
        #     print("Dropdown options:", available_states)

        #     for option in dropdown_options:
        #         if option.text.strip().endswith(city_name):  
        #             ActionChains(driver).move_to_element(option).click().perform()
        #             time.sleep(2)
        #             break
        #     else:
        #         print(f"State '{city_name}' not found in dropdown!")


        # except Exception as e:
        #     print(f"Error: {e}")

        # # Fill in remaining form fields
        # driver.find_element(By.NAME, "pincode").send_keys(row["pincode"])
        # driver.find_element(By.NAME, "address").send_keys(row["address"])
        for field_name in ["branch_name", "contact", "gst_no", "pincode", "address"]:
            try:
                field = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.NAME, field_name))
                )
                field.clear()
                field.send_keys(str(row[field_name]))
                time.sleep(0.5)
            except Exception as e:
                print(f"Error filling {field_name}: {e}")

        # Fill autocomplete fields
        clear_and_fill_autocomplete(driver, "country-select", row["country"])
        clear_and_fill_autocomplete(driver, "state-select", row["state"])
        clear_and_fill_autocomplete(driver, "city-select", row["city"])

        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Error clicking Confirm button: {e}")



        # button = WebDriverWait(driver, 5).until(
        #     EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
        # )
        # button.click()
        # time.sleep(2)



if __name__ == "__main__":

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("vaishnavi")
    driver.find_element(By.NAME, "login").click()
    time.sleep(5)

    driver.find_element(By.ID, "long-button").click()
    view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    view_button.click()
    time.sleep(2)

    fill_branch_forms(driver)
    time.sleep(5)
    driver.quit()
    print("Purchase form submission done.")






# # Wait for a few seconds before quitting
# time.sleep(15)
# driver.quit()
# print("Done")
