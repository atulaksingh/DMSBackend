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
    df = pd.read_excel(r"bank500.xlsx")  # Modify path as needed

    # try:
    #     tab = WebDriverWait(driver, 5).until(
    #         EC.presence_of_element_located((By.XPATH, "//*[text()='Bank Details']"))
    #     )
    #     driver.execute_script("arguments[0].scrollIntoView(true);", tab)
    #     WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
    #     driver.execute_script("arguments[0].click();", tab)
    # except TimeoutException:
    #     print("Owner Details tab not found!")
    df = df[df["client_id"].notna()]  # Skip rows with NaN
    df["client_id"] = df["client_id"].astype(int)

    grouped = df.groupby("client_id")

    for client_id, group in grouped:
        print(f"Processing client_id: {client_id}")

        try:
            driver.get(f"http://localhost:5173/clientDetails/{client_id}")
            time.sleep(2)

            tab = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Bank Details']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", tab)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
            driver.execute_script("arguments[0].click();", tab)

        except TimeoutException:
            print(f"Bank Details tab not found for client {client_id}!")
            continue

        # for index, row in df.iterrows():
        for index, row in group.iterrows():
            print(f"Filling bank form for row {index} of client {client_id}")

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
                # fields = {
                #     "account_no": row["account_no"],
                #     "bank_name": row["bank_name"],
                #     "account_type": row["account_type"],
                #     "branch": row["branch"],
                #     "ifsc": row["ifsc"],
                #     "files": [row["file1"], row["file2"]]
                # }

                # for field_name, value in fields.items():
                #     elem = driver.find_element(By.NAME, field_name)
                #     elem.clear()
                #     elem.send_keys(value)
                driver.find_element(By.NAME, "account_no").send_keys(row["account_no"])
                driver.find_element(By.NAME, "bank_name").send_keys(row["bank_name"])
                driver.find_element(By.NAME, "account_type").send_keys(row["account_type"])
                driver.find_element(By.NAME, "branch").send_keys(row["branch"])
                driver.find_element(By.NAME, "ifsc").send_keys(row["ifsc"])
                file_input = driver.find_element(By.NAME, 'files')
                file_input.send_keys(row["file1"])
                file_input.send_keys(row["file2"])
                
                
                wait = WebDriverWait(driver, 2)

                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]")))
                button.click()

            except Exception as e:
                print(f"Error filling bank form for row {index}: {e}")
                continue

            time.sleep(2)

    print("All bank processed for all clients.")

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

    fill_bank_forms(driver)
    time.sleep(2)
    driver.quit()
    print("Bank form submission done.")
