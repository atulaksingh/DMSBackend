import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
# import officelocation  # optional if you want to call it later
import customeruser

def fill_clientuser_forms(driver):
    # Load the Excel data
    df = pd.read_excel(r"user100.xlsx")

    # Map column names to lowercase without spaces for convenience
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Click on 'Users Creation' tab
    try:
        time.sleep(10)
        tab = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Users Creation']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(2)
    except TimeoutException:
        print("Users Creation tab not found!")

    for index, row in df.iterrows():
        try:
            # Wait for backdrop to disappear
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
            )

            # Click the 'Create' button
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            driver.execute_script("arguments[0].click();", button)

        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"Error clicking Create button: {e}")
            continue

        time.sleep(2)  # wait for form to appear

        try:
            # Fill form fields
            # driver.find_element(By.NAME, "first_name").send_keys(row["first_name"])
            # driver.find_element(By.NAME, "last_name").send_keys(row["last_name"])
            # driver.find_element(By.NAME, "email").send_keys(row["email"])
            # driver.find_element(By.NAME, "password").send_keys(row["password"])

            fields = {
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password": row["password"]
            }

            for field_name, value in fields.items():
                elem = driver.find_element(By.NAME, field_name)
                elem.clear()              # clear any existing data
                elem.send_keys(str(value))  # fill fresh data

            # Click Confirm button
            confirm_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
            driver.execute_script("arguments[0].click();", confirm_button)

            try:
                error_elem = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'required') or contains(text(), 'can only contain alphabets and spaces') or contains(text(), 'must be') or contains(text(), 'Invalid')]"
                    ))
                )
                error_text = error_elem.text.strip()
                print(f"Error for row {index}, client: {error_text}")               
                # Always cancel modal
                try:
                    cancel_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.NAME, "clientuser_cancel"))
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
                    EC.element_to_be_clickable((By.NAME, "clientuser_cancel"))
                )
                cancel_btn.click()
                print("Modal cancelled after exception during filling.")
                time.sleep(1)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue

        time.sleep(2)  # small pause before next user

    customeruser.fill_customeruser_forms(driver)

if __name__ == "__main__":
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    # Login
    driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("vaishnavi")
    driver.find_element(By.NAME, "login").click()
    time.sleep(3)

    # Open menu
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

    fill_clientuser_forms(driver)

    time.sleep(3)
    driver.quit()
    print("User form submission done.")
