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
import branchdoc
import user
import companydoc
import taxaudit
import air
import sft
import tdspayment 
import tdsreturn
import others
import customer
import purchase
import sales
import income
import expenses
import zip_upload
import ack




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
    df = df.iloc[10:] 

    try:
        time.sleep(10)
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

        try:
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
            
            try:
                error_elem = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'required') or contains(text(), 'must be') or contains(text(), 'can only contain alphabets and spaces')]"
                    ))
                )
                error_text = error_elem.text.strip()
                print(f"Error for row {index}, client: {error_text}")               
                # Always cancel modal
                try:
                    cancel_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.NAME, "branch_cancel"))
                    )
                    cancel_btn.click()
                    time.sleep(1)
                except TimeoutException:
                    print("Cancel button not found after error!")

            except TimeoutException:
                # No error → assume success
                print(f"Row {index} for client submitted successfully.")
        except Exception as e:
            print(f"Error filling bank form for row {index}: {e}")
            # continue
            try:
                cancel_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.NAME, "branch_cancel"))
                )
                cancel_btn.click()
                print("Modal cancelled after exception during filling.")
                time.sleep(1)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue


        time.sleep(2)
    # branchdoc.fill_branchdoc_forms(driver)
    # user.fill_clientuser_forms(driver)
    # companydoc.fill_companydoc_forms(driver)
    # taxaudit.fill_taxaudit_forms(driver)
    # air.fill_air_forms(driver)
    # sft.fill_sft_forms(driver)
    # tdspayment.fill_tdspayment_forms(driver)
    tdsreturn.fill_tdsreturn_forms(driver)
    others.fill_others_forms(driver)
    customer.fill_customer_forms(driver)
    purchase.fill_purchase_forms(driver)
    sales.fill_sales_forms(driver)
    income.fill_income_forms(driver)
    expenses.fill_expenses_forms(driver)
    zip_upload.fill_zip_upload_forms(driver)
    ack.fill_ack_forms(driver)
    driver.find_element(By.NAME, "clientview-btn").click()
    time.sleep(2)

    

if __name__ == "__main__":

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("vaishnavi")
    driver.find_element(By.NAME, "login").click()
    time.sleep(3)

    # driver.find_element(By.ID, "long-button").click()
    # view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    # view_button.click()
    # time.sleep(2)
    client_name = "Quamba"
    print("AAAA",client_name)

    

    client_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{client_name}')]"))
    )

    row_element = client_element.find_element(By.XPATH, "./ancestor::tr")

    # Open menu for this row
    menu_button = row_element.find_element(By.ID, "long-button")
    driver.execute_script("arguments[0].click();", menu_button)

    # Click View
    view_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'View')]"))
    )
    driver.execute_script("arguments[0].click();", view_button)


    fill_branch_forms(driver)
    time.sleep(3)
    driver.quit()
    print("Purchase form submission done.")






# # Wait for a few seconds before quitting
# time.sleep(15)
# driver.quit()
# print("Done")
