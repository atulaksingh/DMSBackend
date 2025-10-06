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
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


def fill_customeruser_forms(driver):

    try:
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Users Creation']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Users Creation tab not found!")

    options = Options()
    options.add_experimental_option("detach", True)  

    df = pd.read_excel(r"customeruser100.xlsx")  

    try:
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='User']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Branch Details tab not found!")

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
            driver.find_element(By.NAME, "first_name").send_keys(row["first_name"])
            driver.find_element(By.NAME, "last_name").send_keys(row["last_name"])
            driver.find_element(By.NAME, "email").send_keys(row["email"])
            driver.find_element(By.NAME, "password").send_keys(row["password"])

            # Click Confirm button
            confirm_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
            driver.execute_script("arguments[0].click();", confirm_button)

            # Optional: call office location function after creating user
            # officelocation.fill_officeloc_forms(driver)


        except Exception as e:
            print(f"Error filling form for row {index}: {e}")
            continue

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

    fill_customeruser_forms(driver)
    time.sleep(5)
    driver.quit()
    print("Purchase form submission done.")
