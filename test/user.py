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
    df = pd.read_excel(r"users.xlsx")

    # Map column names to lowercase without spaces for convenience
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Click on 'Users Creation' tab
    try:
        tab = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Users Creation']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(2)
    except TimeoutException:
        print("Users Creation tab not found!")

    for index, row in df.iterrows():
        try:
            # Wait for backdrop to disappear
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
            )

            # Click the 'Create' button
            button = WebDriverWait(driver, 10).until(
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
            driver.find_element(By.NAME, "first_name").send_keys(row["first_name"])
            driver.find_element(By.NAME, "last_name").send_keys(row["last_name"])
            driver.find_element(By.NAME, "email").send_keys(row["email"])
            driver.find_element(By.NAME, "password").send_keys(row["password"])

            # Click Confirm button
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
            driver.execute_script("arguments[0].click();", confirm_button)

            # Optional: call office location function after creating user
            # officelocation.fill_officeloc_forms(driver)


        except Exception as e:
            print(f"Error filling form for row {index}: {e}")
            continue

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
    time.sleep(5)

    # Open menu
    driver.find_element(By.ID, "long-button").click()
    view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    view_button.click()
    time.sleep(2)

    fill_clientuser_forms(driver)

    time.sleep(5)
    driver.quit()
    print("User form submission done.")
