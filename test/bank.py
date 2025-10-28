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
from selenium.common.exceptions import TimeoutException


def fill_bank_forms(driver):
    df = pd.read_excel(r"bank200.xlsx")  # Modify path as needed

    try:
        time.sleep(10)
        tab = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Bank Details']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Owner Details tab not found!")

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
        time.sleep(2)

        try:
            # driver.find_element(By.NAME, "account_no").send_keys(row["account_no"])
            # driver.find_element(By.NAME, "bank_name").send_keys(row["bank_name"])
            # driver.find_element(By.NAME, "account_type").send_keys(row["account_type"])
            # driver.find_element(By.NAME, "branch").send_keys(row["branch"])
            # driver.find_element(By.NAME, "ifsc").send_keys(row["ifsc"])
            
            # file_input = driver.find_element(By.NAME, 'files')
            # file_input.send_keys(row["file1"])
            # file_input.send_keys(row["file2"])
            # file_input.send_keys(row["file3"])

            fields = {
                "account_no": row["account_no"],
                "bank_name": row["bank_name"],
                "account_type": row["account_type"],
                "branch": row["branch"],
                "ifsc": row["ifsc"],
                # "files": [row["file1"]]
            }
            

            for field_name, value in fields.items():
                elem = driver.find_element(By.NAME, field_name)
                elem.clear()              # clear any existing data
                elem.send_keys(str(value))  # fill fresh data

            file_input = driver.find_element(By.NAME, 'files')
            file_input.clear()
            file_input.send_keys(row["file1"])
            file_input.send_keys(row["file2"])


            wait = WebDriverWait(driver, 1)

            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]")))
            button.click()

            try:
                error_elem = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'required') or contains(text(), 'must be')]"
                    ))
                )
                error_text = error_elem.text.strip()
                print(f"Error for row {index}, client: {error_text}")               
                # Always cancel modal
                try:
                    cancel_btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.NAME, "bank_cancel"))
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
                    EC.element_to_be_clickable((By.NAME, "bank_cancel"))
                )
                cancel_btn.click()
                print("Modal cancelled after exception during filling.")
                time.sleep(1)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue


        # time.sleep(3)

if __name__ == "__main__":

    # 65555555555555

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

    fill_bank_forms(driver)
    time.sleep(3)
    driver.quit()
    print("Bank form submission done.")
