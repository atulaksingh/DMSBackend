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


def fill_tdspayment_forms(driver):
    df = pd.read_excel(r"tdspayment200.xlsx")
    # df = df.iloc[53:] 


    try:
        time.sleep(10)
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Documents']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Documents tab not found!")

    # Convert date_of_incorporation to MM-DD-YYYY format
    # df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%m-%d-%Y")
    # df["TDS Payment Date"] = pd.to_datetime(df["TDS Payment Date"]).dt.strftime("%m-%d-%Y")
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True).dt.strftime("%d/%m/%Y").str.replace(r'\b0', '', regex=True)
    df["TDS Payment Date"] = pd.to_datetime(df["TDS Payment Date"], dayfirst=True).dt.strftime("%d/%m/%Y").str.replace(r'\b0', '', regex=True)


    for index, row in df.iterrows():

        print(list(df.columns))  # Check exact column names

        button = driver.find_element(By.XPATH, "//button[normalize-space()='TDS Payments']")
        driver.execute_script("arguments[0].click();", button)

        # Create button
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Create']"))
        )
        button.click()

        try:
            # Client name
            # driver.find_element(By.NAME, "client_name").send_keys(row["Client Name"])

            # Date (Handling MM-DD-YYYY format)
            date_input = driver.find_element(By.NAME, "date")
            date_input.click()
            time.sleep(1)  # Allow calendar to open
            date_input.send_keys(Keys.CONTROL + "a")  # Select existing date (if any)
            date_input.send_keys(Keys.BACKSPACE)  # Clear existing date
            date_input.send_keys(row["Date"])  # Enter date in MM-DD-YYYY format
            date_input.send_keys(Keys.ENTER)  # Confirm selection

            fields = {
                "client_name": row["Client Name"],
                "PAN": row["PAN"],
                "amount": row["Amount"],
                "cgst": row["CGST"],
                "sgst": row["SGST"],
                "igst": row["IGST"],
                "total_amt": row["Total Amount"],
                "tds_rate": row["TDS Rate"],
                "tds_challan_no": row["TDS Challan"],
                "tds_amount": row["TDS Amount"],
                "net_amount": row["Net Amount"]
            }

            for field_name, value in fields.items():
                elem = driver.find_element(By.NAME, field_name)
                elem.clear()              # clear any existing data
                elem.send_keys(str(value))  # fill fresh data
           
            date_input = driver.find_element(By.NAME, "tds_payment_date")
            date_input.click()
            time.sleep(1)  # Allow calendar to open
            date_input.send_keys(Keys.CONTROL + "a")  # Select existing date (if any)
            date_input.send_keys(Keys.BACKSPACE)  # Clear existing date
            date_input.send_keys(row["TDS Payment Date"])  # Enter date in MM-DD-YYYY format
            date_input.send_keys(Keys.ENTER)  # Confirm selection

            # TDS Challan No
            # driver.find_element(By.NAME, "tds_challan_no").send_keys(row["TDS Challan"])

            # TDS Section
            dropdown = driver.find_element(By.NAME, "tds_section")
            dropdown.click()
            tds_section =  row["TDS Section"]
            option_xpath = f"//li[text()='{tds_section}']"
            # option = driver.find_element(By.XPATH, option_xpath)
            option = WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, option_xpath))
            )
            option.click()
            time.sleep(2)


            # Submit button
            button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            button.click()
            time.sleep(2)

            try:
                error_elem = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'required') or contains(text(), 'can only contain alphabets and spaces') or contains(text(), 'must be') or contains(text(), 'valid number')]"
                    ))
                )
                error_text = error_elem.text.strip()
                print(f"Error for row {index}, client: {error_text}")               
                # Always cancel modal
                try:
                    cancel_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.NAME, "tdspayment_cancel"))
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
                    EC.element_to_be_clickable((By.NAME, "tdspayment_cancel"))
                )
                cancel_btn.click()
                print("Modal cancelled after exception during filling.")
                time.sleep(1)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue


if __name__ == "__main__":
    # This block allows you to run owner.py standalone for testing.
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

    fill_tdspayment_forms(driver)
    time.sleep(15)
    driver.quit()
    print("TDS Payment form submission done.")
