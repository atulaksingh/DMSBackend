import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import officelocation
from selenium.common.exceptions import TimeoutException


# def fill_branchdoc_forms(driver):
#     # Load the Excel data
#     df = pd.read_excel(r"doc.xlsx")


#     try:
#         tab = WebDriverWait(driver, 5).until(
#             EC.presence_of_element_located((By.XPATH, "//*[text()='Branch Details']"))
#         )
#         driver.execute_script("arguments[0].scrollIntoView(true);", tab)
#         WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
#         driver.execute_script("arguments[0].click();", tab)
#     except TimeoutException:
#         print("Branch Details tab not found!")


#     # Wait for branch table to load
#     WebDriverWait(driver, 5).until(
#         EC.presence_of_element_located((By.XPATH, "//table"))
#     )

#     # Get all branch rows
#     branch_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'MuiTableRow-root MuiTableRow-hover')]")

#     print(f"Total Branches Found: {len(branch_rows)}")

#     for i in range(len(branch_rows)):
#         # Re-fetch the list of branches to avoid stale elements
#         branch_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'MuiTableRow-root MuiTableRow-hover')]")

#         if i >= len(branch_rows):
#             print(f"Branch index {i} out of range, stopping loop.")
#             break

#         try:
#             view_button = branch_rows[i].find_element(By.XPATH, ".//button[@id='long-button']")
#             driver.execute_script("arguments[0].scrollIntoView();", view_button)  # Scroll if not visible
#             time.sleep(1)
#             view_button.click()
#             time.sleep(2)

#             # Click the dropdown option (assuming it's the first option)
#             dropdown_option = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root"))
#             )
#             dropdown_option.click()
#             time.sleep(3)

#             print(f"Opened Branch {i + 1}")

#         except Exception as e:
#             print(f"Error clicking View button for Branch {i + 1}: {e}")
#             continue

#         # Add 10 branch document records for this branch
#         for index, row in df.iterrows():
#             try:
#                 button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
#                 button.click()
#             except Exception as e:
#                 print(f"Error clicking Create button: {e}")
#                 continue
#             time.sleep(5)

#             try:

#                 dropdown = driver.find_element(By.NAME, "document_type")
#                 dropdown.click()

#                 document_type =  row["Document Type"]
#                 document_type = document_type.upper()

#                 option_xpath = f"//li[text()='{document_type}']"
#                 option = driver.find_element(By.XPATH, option_xpath)
#                 option.click()
#                 time.sleep(2)
#                 driver.find_element(By.NAME, "login").send_keys(row["Login"])
#                 driver.find_element(By.NAME, "password").send_keys(row["Password"])
#                 driver.find_element(By.NAME, "remark").send_keys(row["Remark"])

#                 file_input = driver.find_element(By.NAME, 'files')
#                 file_input.send_keys(row["File1"])
#                 file_input.send_keys(row["File2"])

#                 button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
#                 )
#                 button.click()

#                 # officelocation.fill_officeloc_forms(driver)

#             except Exception as e:
#                 print(f"Error filling form for row {index}: {e}")
#                 continue

            
#             time.sleep(5)
        
#         officelocation.fill_officeloc_forms(driver)


#         # Navigate back to the branch list before going to the next branch
#         print(f"Exiting Branch {i + 1}...")



#         button = driver.find_element(By.CSS_SELECTOR, "a[href*='/clientDetails']")
#         button.click()
#         time.sleep(2)
#         try:
#             tab = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.XPATH, "//*[text()='Branch Details']"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", tab)
#             WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
#             driver.execute_script("arguments[0].click();", tab)
#         except TimeoutException:
#             print("Branch Details tab not found!")


def fill_branchdoc_forms(driver):
    # Load the Excel data
    
    df = pd.read_excel(r"branchdoc500.xlsx")

    for index, row in df.iterrows():
        try:
            tab = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Branch Details']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", tab)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
            driver.execute_script("arguments[0].click();", tab)
        except TimeoutException:
            print("Branch Details tab not found!")
            return

        # Wait for branch table
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )
        
        branch_name = row["Branch_name"]   # ✅ This fetches Borivali (or whatever is in Excel)

        print(f"Creating branch: {branch_name}")

        try:
            client_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{branch_name}')]"))
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

        except Exception as e:
            print(f"Branch '{branch_name}' not found in UI: {e}")
        
        time.sleep(3)
        try:
            create_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
            )
            create_btn.click()
            time.sleep(2)

            # Fill dropdown
            dropdown = driver.find_element(By.NAME, "document_type")
            dropdown.click()
            document_type = row["Document Type"].strip()
            option_xpath = f"//li[normalize-space(text())='{document_type}']"
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            option.click()

            # Fill inputs
            driver.find_element(By.NAME, "login").send_keys(row["Login"])
            driver.find_element(By.NAME, "password").send_keys(row["Password"])
            driver.find_element(By.NAME, "remark").send_keys(row["Remark"])

            # Upload files
            file_input = driver.find_element(By.NAME, 'files')
            if pd.notna(row["File1"]):
                file_input.send_keys(row["File1"])
            if pd.notna(row["File2"]):
                file_input.send_keys(row["File2"])

            # Confirm
            confirm_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            confirm_btn.click()
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='ClientDetails']"))
            )
            element.click()
            time.sleep(3)


            print(f"✅ Added BranchDoc row {index+1} for {branch_name}")

        except Exception as e:
            print(f"❌ Error filling doc row {index+1}: {e}")
            continue

        time.sleep(3)

    # Call office location fill if needed
    # officelocation.fill_officeloc_forms(driver)

    # Return back to Branch Details list
    try:
        back_btn = driver.find_element(By.CSS_SELECTOR, "a[href*='/clientDetails']")
        back_btn.click()
        time.sleep(2)
        # reopen Branch tab
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Branch Details']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        driver.execute_script("arguments[0].click();", tab)
    except Exception as e:
        print(f"⚠️ Could not navigate back: {e}")


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

    fill_branchdoc_forms(driver)
    time.sleep(5)
    driver.quit()
    print("Purchase form submission done.")


