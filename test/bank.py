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

def fill_bank_forms(driver):
    df = pd.read_excel(r"bank2.xlsx")  # Modify path as needed

    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Bank Details')]")
    button.click()

    for index, row in df.iterrows():
        print(list(df.columns))  # Check exact column names

        try:
            button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
            if button.is_displayed() and button.is_enabled():
                button.click()
            else:
                print("Button is not clickable due to being obscured or disabled")
        except Exception as e:
            print(f"Error clicking Create button: {e}")
            continue
        time.sleep(5)

        try:
            driver.find_element(By.NAME, "account_no").send_keys(row["account_no"])
            driver.find_element(By.NAME, "bank_name").send_keys(row["bank_name"])
            driver.find_element(By.NAME, "account_type").send_keys(row["account_type"])
            driver.find_element(By.NAME, "branch").send_keys(row["branch"])
            driver.find_element(By.NAME, "ifsc").send_keys(row["ifsc"])
            # driver.find_element(By.NAME, "it_password").send_keys(row["it_password"])
            # driver.find_element(By.NAME, "mobile").send_keys(row["mobile"])

            file_input = driver.find_element(By.NAME, 'files')
            file_input.send_keys(row["file1"])
            file_input.send_keys(row["file2"])
            # file_input.send_keys(row["file3"])

            wait = WebDriverWait(driver, 2)

            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]")))
            button.click()

        except Exception as e:
            print(f"Error filling bank form for row {index}: {e}")
            continue

        time.sleep(5)
