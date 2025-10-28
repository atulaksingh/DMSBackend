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


def fill_customer_forms(driver):
    df = pd.read_excel(r"customervendor20.xlsx") 

    try:
        time.sleep(10)
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Customer&Vendor']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Customer Vendor tab not found!")

    for index, row in df.iterrows():
        try:
            print(list(df.columns))  # Check exact column names

            # button = WebDriverWait(driver, 5).until(
            #     EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Create']"))
            # )
            # button.click()
            button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]").click()
            time.sleep(1)

            fields = {
                "name": row["name"],
                "gst_no": row["gst_no"],
                "pan": row["pan"],
                "email": row["email"],
                "contact": str(row["contact"]),  # Ensure contact is treated as string
                "address": row["address"],
            }

            for field_name, value in fields.items():
                elem = driver.find_element(By.NAME, field_name)
                elem.clear()              # clear any existing data
                elem.send_keys(str(value)) 

            # driver.find_element(By.NAME, "name").send_keys(row["name"])
            # driver.find_element(By.NAME, "gst_no").send_keys(row["gst_no"])
            # driver.find_element(By.NAME, "pan").send_keys(row["pan"])
            # driver.find_element(By.NAME, "email").send_keys(row["email"])
            # driver.find_element(By.NAME, "contact").send_keys(row["contact"])
            # driver.find_element(By.NAME, "address").send_keys(row["address"])

            customer = row["customer"]
            vendor = row["vendor"]

            # Check if 'customer' is True, then click the checkbox
            customer_checkbox = driver.find_element(By.NAME, "customer")
            if customer:  # If customer is True
                if not customer_checkbox.is_selected():  # Check if it's not already selected
                    customer_checkbox.click()
            else:
                if customer_checkbox.is_selected():  # If it was selected, unselect it
                    customer_checkbox.click()

            # Check if 'vendor' is True, then click the checkbox
            vendor_checkbox = driver.find_element(By.NAME, "vendor")
            if vendor:  # If vendor is True
                if not vendor_checkbox.is_selected():
                    vendor_checkbox.click()
            else:
                if vendor_checkbox.is_selected():
                    vendor_checkbox.click()
    #
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            button.click()
            time.sleep(2)

            try:
                error_elem = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'required') or contains(text(), 'can only contain alphabets and spaces') or contains(text(), 'must be') or contains(text(), 'invalid')]"
                    ))
                )
                error_text = error_elem.text.strip()
                print(f"Error for row {index}, client: {error_text}")               
                # Always cancel modal
                try:
                    cancel_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.NAME, "cv_cancel"))
                    )
                    cancel_btn.click()
                    time.sleep(1)
                except TimeoutException:
                    print("Cancel button not found after error!")

            except TimeoutException:
                # No error → assume success
                print(f"Row {index} for client submitted successfully.")
        except Exception as e:
            print(f"Error filling form for row {index}: {e}")
            # continue
            try:
                cancel_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.NAME, "cv_cancel"))
                )
                cancel_btn.click()
                print("Modal cancelled after exception during filling.")
                time.sleep(1)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue
        

if __name__ == "__main__":
    # This block allows you to run owner.py standalone for testing.
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("vaishnavi")
    driver.find_element(By.NAME, "login").click()
    time.sleep(3)

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

    # Here you might need to navigate to the owner form page.
    # time.sleep(3)  # Adjust waiting time as needed.
    fill_customer_forms(driver)
    time.sleep(3)
    driver.quit()
    print("Customer or Vendor form submission done.")
