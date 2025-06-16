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
    df = pd.read_excel(r"cus.xlsx") 

    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Customer Vendor')]")
    button.click()

    for index, row in df.iterrows():

        print(list(df.columns))  # Check exact column names

        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]").click()
        time.sleep(1)

        driver.find_element(By.NAME, "name").send_keys(row["name"])
        driver.find_element(By.NAME, "gst_no").send_keys(row["gst_no"])
        driver.find_element(By.NAME, "pan").send_keys(row["pan"])
        driver.find_element(By.NAME, "email").send_keys(row["email"])
        driver.find_element(By.NAME, "contact").send_keys(row["contact"])
        driver.find_element(By.NAME, "address").send_keys(row["address"])

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

if __name__ == "__main__":
    # This block allows you to run owner.py standalone for testing.
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.ID, "long-button").click()
    view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    view_button.click()
    time.sleep(2)

    # Here you might need to navigate to the owner form page.
    # time.sleep(5)  # Adjust waiting time as needed.
    fill_customer_forms(driver)
    time.sleep(15)
    driver.quit()
    print("Customer or Vendor form submission done.")
