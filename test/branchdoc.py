import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import officelocation

def fill_branchdoc_forms(driver):
    # Load the Excel data
    df = pd.read_excel(r"doc.xlsx")


    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Branch Details')]")
    button.click()
    time.sleep(3)


    # Wait for branch table to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )

    # Get all branch rows
    branch_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'MuiTableRow-root MuiTableRow-hover')]")

    print(f"Total Branches Found: {len(branch_rows)}")

    for i in range(len(branch_rows)):
        # Re-fetch the list of branches to avoid stale elements
        branch_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'MuiTableRow-root MuiTableRow-hover')]")

        if i >= len(branch_rows):
            print(f"Branch index {i} out of range, stopping loop.")
            break

        try:
            view_button = branch_rows[i].find_element(By.XPATH, ".//button[@id='long-button']")
            driver.execute_script("arguments[0].scrollIntoView();", view_button)  # Scroll if not visible
            time.sleep(1)
            view_button.click()
            time.sleep(2)

            # Click the dropdown option (assuming it's the first option)
            dropdown_option = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root"))
            )
            dropdown_option.click()
            time.sleep(3)

            print(f"Opened Branch {i + 1}")

        except Exception as e:
            print(f"Error clicking View button for Branch {i + 1}: {e}")
            continue

        # Add 10 branch document records for this branch
        for index, row in df.iterrows():
            try:
                button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
                button.click()
            except Exception as e:
                print(f"Error clicking Create button: {e}")
                continue
            time.sleep(5)

            try:

                dropdown = driver.find_element(By.NAME, "document_type")
                dropdown.click()

                document_type =  row["Document Type"]
                document_type = document_type.upper()

                option_xpath = f"//li[text()='{document_type}']"
                option = driver.find_element(By.XPATH, option_xpath)
                option.click()
                time.sleep(2)
                driver.find_element(By.NAME, "login").send_keys(row["Login"])
                driver.find_element(By.NAME, "password").send_keys(row["Password"])
                driver.find_element(By.NAME, "remark").send_keys(row["Remark"])

                file_input = driver.find_element(By.NAME, 'files')
                file_input.send_keys(row["File1"])
                file_input.send_keys(row["File2"])

                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
                )
                button.click()

                officelocation.fill_officeloc_forms(driver)

            except Exception as e:
                print(f"Error filling form for row {index}: {e}")
                continue

            time.sleep(5)

        # Navigate back to the branch list before going to the next branch
        print(f"Exiting Branch {i + 1}...")

        client_details_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/clientDetails/')]"))
        )
        client_details_link.click()
        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Branch Details')]")
        button.click()
        time.sleep(3)


# time.sleep(5)
# driver.quit()
# print("All forms submitted successfully!")
