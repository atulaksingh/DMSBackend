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


def fill_ack_forms(driver):
    df = pd.read_excel(r"ack200.xlsx") 

    try:
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Acknowledgement']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Acknowledgement tab not found!")

    # Convert date_of_incorporation to MM-DD-YYYY format
    df["from_date"] = pd.to_datetime(df["from_date"]).dt.strftime("%m-%d-%Y")
    df["to_date"] = pd.to_datetime(df["to_date"]).dt.strftime("%m-%d-%Y")

    for index, row in df.iterrows():

        print(list(df.columns))  # Check exact column names

        # Create button
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Create']"))
        )
        button.click()
        
        # Return number
        dropdown = driver.find_element(By.NAME, "return_type")
        dropdown.click()
        return_type =  row["Return Type"]
        option_xpath = f"//li[text()='{return_type}']"
        option = driver.find_element(By.XPATH, option_xpath)
        option.click()
        time.sleep(2)

        # Frequency
        dropdown = driver.find_element(By.NAME, "frequency")
        dropdown.click()
        frequency =  row["Frequency"]
        option_xpath = f"//li[text()='{frequency}']"
        option = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, option_xpath))
        )
        option.click()
        time.sleep(2)


        # From Date (Handling MM-DD-YYYY format)
        date_input = driver.find_element(By.NAME, "from_date")
        date_input.click()
        time.sleep(1)  # Allow calendar to open
        date_input.send_keys(Keys.CONTROL + "a")  # Select existing date (if any)
        date_input.send_keys(Keys.BACKSPACE)  # Clear existing date
        date_input.send_keys(row["from_date"])  # Enter date in MM-DD-YYYY format
        date_input.send_keys(Keys.ENTER)  # Confirm selection

        # To Date (Handling MM-DD-YYYY format)
        date_input = driver.find_element(By.NAME, "to_date")
        date_input.click()
        time.sleep(1)  # Allow calendar to open
        date_input.send_keys(Keys.CONTROL + "a")  # Select existing date (if any)
        date_input.send_keys(Keys.BACKSPACE)  # Clear existing date
        date_input.send_keys(row["to_date"])  # Enter date in MM-DD-YYYY format
        date_input.send_keys(Keys.ENTER)  # Confirm selection

        # Month
        driver.find_element(By.NAME, "month").send_keys(row["month"])

        # Client Review
        dropdown = driver.find_element(By.NAME, "client_review")
        dropdown.click()
        client_review =  row["Client Review"]
        option_xpath = f"//li[text()='{client_review}']"
        option = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.XPATH, option_xpath))
        )
        option.click()
        time.sleep(2)


        # Computation file upload handling
        file_input = driver.find_element(By.NAME, 'computation_file')
        file_input.send_keys(row["file1"])

        # Return file upload handling
        file_input = driver.find_element(By.NAME, 'return_file')
        file_input.send_keys(row["file2"])

        # Submit button
        button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
        )
        button.click()
        time.sleep(2)

if __name__ == "__main__":
    # This block allows you to run owner.py standalone for testing.
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

    fill_ack_forms(driver)
    time.sleep(5)
    driver.quit()
    print("Acknowledgment form submission done.")
