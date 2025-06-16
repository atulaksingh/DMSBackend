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


def fill_zip_upload_forms(driver):
    # options = Options()
    # options.add_experimental_option("detach", True)  

    df = pd.read_excel(r"zipupload.xlsx")  

    # button = driver.find_element(By.XPATH, "//button[contains(text(), 'ZipFile  Upload')]")
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'ZipFile  Upload')]")
    time.sleep(10)
    button.click()

    # Loop through the rows in the dataframe
    for index, row in df.iterrows():
        print(list(df.columns))  # Check exact column names

        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Upload Invoice')]").click()
        time.sleep(15)

        file_input = driver.find_element(By.NAME, 'file')
        file_input.send_keys(row["File1"])
        file_input.send_keys(row["File2"])


        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
        )
        button.click()
        time.sleep(2)



if __name__ == "__main__":

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.ID, "long-button").click()
    view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    view_button.click()
    time.sleep(2)

    fill_zip_upload_forms(driver)
    time.sleep(1)
    driver.quit()
    print("ZipFile Upload form submission done.")






# # Wait for a few seconds before quitting
# time.sleep(15)
# driver.quit()
# print("Done")
