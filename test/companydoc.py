import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
# import officelocation
import tdspayment 
import tdsreturn
import others
import customer
import purchase
import sales
import income
import expenses
import zip_upload
import ack

def fill_companydoc_forms(driver):
    # Load the Excel data
    df = pd.read_excel(r"companydoc50.xlsx")
    # df = df.iloc[50:] 


    # button = driver.find_element(By.XPATH, "//button[contains(text(), 'Company Documents')]")
    # button.click()
    # time.sleep(3)

    try:
        time.sleep(10)
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Company Documents']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Company Documents tab not found!")



    # Wait for branch table to load
    
    WebDriverWait(driver, 20).until(
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

        # try:
        #     view_button = branch_rows[i].find_element(By.XPATH, ".//button[@id='long-button']")
        #     driver.execute_script("arguments[0].scrollIntoView();", view_button)  # Scroll if not visible
        #     time.sleep(1)
        #     view_button.click()
        #     time.sleep(2)

        #     # Click the dropdown option (assuming it's the first option)
        #     dropdown_option = WebDriverWait(driver, 5).until(
        #         EC.presence_of_element_located((By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root"))
        #     )
        #     dropdown_option.click()
        #     time.sleep(3)

        #     print(f"Opened Branch {i + 1}")

        # except Exception as e:
        #     print(f"Error clicking View button for Branch {i + 1}: {e}")
        #     continue

        # Add 10 branch document records for this branch
        for index, row in df.iterrows():
            try:
                button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
                button.click()
            except Exception as e:
                print(f"Error clicking Create button: {e}")
                continue
            time.sleep(3)

            try:

                dropdown = driver.find_element(By.NAME, "document_type")
                dropdown.click()

                document_type =  row["Document Type"]
                # document_type = document_type.upper()

                option_xpath = f"//li[text()='{document_type}']"
                option = driver.find_element(By.XPATH, option_xpath)
                option.click()
                time.sleep(2)
                # driver.find_element(By.NAME, "login").send_keys(row["Login"])
                # driver.find_element(By.NAME, "password").send_keys(row["Password"])
                # driver.find_element(By.NAME, "remark").send_keys(row["Remark"])
                fields = {
                    "login": row["Login"],
                    "password": row["Password"],
                    "remark": row["Remark"]
                }   
                for field_name, value in fields.items():
                    elem = driver.find_element(By.NAME, field_name)
                    elem.clear()              # clear any existing data
                    elem.send_keys(str(value))  # fill fresh data


                file_input = driver.find_element(By.NAME, 'files')
                file_input.clear()
                file_input.send_keys(row["File1"])
                file_input.send_keys(row["File2"])

                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
                )
                button.click()
                try:
                    error_elem = WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located((
                            By.XPATH,
                            "//*[contains(text(), 'required') or contains(text(), 'one file is required') or contains(text(), 'must be') or contains(text(), 'Invalid')]"
                        ))
                    )
                    error_text = error_elem.text.strip()
                    print(f"Error for row {index}, client: {error_text}")               
                    # Always cancel modal
                    try:
                        cancel_btn = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.NAME, "companydoc_cancel"))
                        )
                        cancel_btn.click()
                        time.sleep(1)
                    except TimeoutException:
                        print("Cancel button not found after error!")

                except TimeoutException:
                    # No error → assume success
                    print(f"Row {index} for client submitted successfully.")


                # officelocation.fill_officeloc_forms(driver)

            except Exception as e:
                print(f"Error filling form for row {index}: {e}")
                # continue
                try:
                    cancel_btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.NAME, "companydoc_cancel"))
                    )
                    cancel_btn.click()
                    time.sleep(2)
                    print("Modal cancelled after exception during filling.")
                    time.sleep(1)

                except TimeoutException:
                    # continue
                    print("Cancel button not found after exception during filling!")
                # continue

            time.sleep(3)

        # Navigate back to the branch list before going to the next branch
        print(f"Exiting Branch {i + 1}...")
    # tdspayment.fill_tdspayment_forms(driver)
    # tdsreturn.fill_tdsreturn_forms(driver)
    # others.fill_others_forms(driver)
    # customer.fill_customer_forms(driver)
    # purchase.fill_purchase_forms(driver)
    # sales.fill_sales_forms(driver)
    # income.fill_income_forms(driver)
    # expenses.fill_expenses_forms(driver)
    # zip_upload.fill_zip_upload_forms(driver)
    # ack.fill_ack_forms(driver)

       

if __name__ == "__main__":

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

    fill_companydoc_forms(driver)
    time.sleep(3)
    driver.quit()
    print("Purchase form submission done.")


# time.sleep(3)
# driver.quit()
# print("All forms submitted successfully!")
