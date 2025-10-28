import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchWindowException,
)

def fill_owner_forms(driver):
    df = pd.read_excel(r"owner200.xlsx")

    try:
        time.sleep(10)
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Owner Details']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)

    except TimeoutException:
        print(f"Owner Details tab not found for client!")
        # continue

    for index, row in df.iterrows():
        try:
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
            )
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
            )
            button.click()
        except (ElementClickInterceptedException, TimeoutException) as e:
            print(f"Error clicking Create button for client, row {index}: {e}")

        try:
            fields = {
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "share": row["share"],
                "pan": row["pan"],
                "aadhar": row["aadhar"],
                "email": row["email"],
                "username": row["username"],
                "it_password": row["it_password"],
                "mobile": row["mobile"],
                "user_password": row["user_password"]
            }

            for field_name, value in fields.items():
                elem = driver.find_element(By.NAME, field_name)
                elem.clear()              # clear any existing data
                elem.send_keys(str(value))  # fill fresh data


            confirm_btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            confirm_btn.click()

            # Wait for error or success
            try:
                error_elem = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'shares') or contains(text(), 'Cannot')]"
                    ))
                )
                error_text = error_elem.text.strip()
                print(f"Error for row {index}, client: {error_text}")

                if "0% shares" in error_text:
                    print(f"Shares exhausted for client , skipping rest of owners.")
                    return     # stop processing this client
                else:
                    print(f"Validation error for client , skipping row {index}.")
                    pass
                
                # Always cancel modal
                try:
                    cancel_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.NAME, "owner_cancel"))
                    )
                    cancel_btn.click()
                    time.sleep(1)
                except TimeoutException:
                    print("Cancel button not found after error!")

            except TimeoutException:
                # No error → assume success
                print(f"Row {index} for client submitted successfully.")

        except Exception as e:
            print(f"Error filling owner form for client , row {index}: {e}")
            # Try cancel if form got stuck
            try:
                cancel_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.NAME, "owner_cancel"))
                )
                cancel_btn.click()
                print("Modal cancelled after exception during filling.")
                time.sleep(1)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue

    print("All owners processed for all clients.")

if __name__ == "__main__":
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("vaishnavi")
    driver.find_element(By.NAME, "login").click()
    time.sleep(2)

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

    fill_owner_forms(driver)
    time.sleep(2)
    driver.quit()
    print("Owner form submission done.")
