import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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
    df = pd.read_excel(r"branch200.xlsx")  
    df = df[df["client_id"].notna()]  # Skip rows with NaN
    df["client_id"] = df["client_id"].astype(int)
    grouped = df.groupby("client_id")

    for client_id, group in grouped:
        print(f"Processing client_id: {client_id}")
        try:
            driver.get(f"http://localhost:5173/clientDetails/{client_id}")
            time.sleep(2)

            tab = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Branch Details']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", tab)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
            driver.execute_script("arguments[0].click();", tab)

        except TimeoutException:
            print(f"Branch Details tab not found for client {client_id}!")
            continue

        for index, row in group.iterrows():
            print(f"Filling Branch form for row {index} of client {client_id}")

            driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]").click()
            time.sleep(1)

            # Clear & fill standard fields
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

            # Click Confirm
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
                )
                button.click()
                time.sleep(2)
            except Exception as e:
                print(f"Error clicking Confirm button: {e}")

    print("All Branch forms processed for all clients.")

if __name__ == "__main__":
    options = Options()
    options.add_experimental_option("detach", True)  

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get("http://localhost:5173/")
    time.sleep(2)

    # Login
    driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("vaishnavi")
    driver.find_element(By.NAME, "login").click()
    time.sleep(3)

    driver.find_element(By.ID, "long-button").click()
    view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    view_button.click()
    time.sleep(2)

    # Fill Branch Forms
    fill_branch_forms(driver)
    time.sleep(3)

    driver.quit()
    print("Branch form submission done.")
