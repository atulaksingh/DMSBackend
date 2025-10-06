import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchWindowException,
)

# def fill_owner_forms(driver):
#     df = pd.read_excel(r"owner500.xlsx")  # Modify path as needed

#     # Ensure client_id is valid integer
#     df = df[df["client_id"].notna()]  # Skip rows with NaN
#     df["client_id"] = df["client_id"].astype(int)

#     grouped = df.groupby("client_id")

#     for client_id, group in grouped:
#         print(f"Processing client_id: {client_id}")

#         try:
#             driver.get(f"http://localhost:5173/clientDetails/{client_id}")
#             time.sleep(2)

#             tab = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.XPATH, "//*[text()='Owner Details']"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", tab)
#             WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
#             driver.execute_script("arguments[0].click();", tab)

#         except TimeoutException:
#             print(f"Owner Details tab not found for client {client_id}!")
#             # continue

#         for index, row in group.iterrows():
#             try:
#                 # Click "Create" button
#                 WebDriverWait(driver, 5).until(
#                     EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
#                 )
#                 button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
#                 )
#                 button.click()
#             except (ElementClickInterceptedException, TimeoutException) as e:
#                 print(f"Error clicking Create button for client {client_id}, row {index}: {e}")
#                 # Force cancel if modal is open
#                 # try:
#                 #     cancel_btn = WebDriverWait(driver, 2).until(
#                 #         EC.element_to_be_clickable((By.NAME, "owner_cancel"))
#                 #     )
#                 #     cancel_btn.click()
#                 #     print("Modal cancelled after Create click error.")
#                 # except TimeoutException:
#                 #     print("Cancel button not found after Create click error!")
#                 # # continue

#             try:
#                 fields = {
#                     "first_name": row["first_name"],
#                     "last_name": row["last_name"],
#                     "share": row["share"],
#                     "pan": row["pan"],
#                     "aadhar": row["aadhar"],
#                     "email": row["email"],
#                     "username": row["username"],
#                     "it_password": row["it_password"],
#                     "mobile": row["mobile"],
#                     "user_password": row["user_password"]
#                 }

#                 for field_name, value in fields.items():
#                     elem = driver.find_element(By.NAME, field_name)
#                     elem.clear()              # clear any existing data
#                     elem.send_keys(str(value))  # fill fresh data


#                 confirm_btn = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
#                 )
#                 confirm_btn.click()

#                 # Wait for error or success
#                 try:
#                     error_elem = WebDriverWait(driver, 3).until(
#                         EC.visibility_of_element_located((
#                             By.XPATH,
#                             "//*[contains(text(), 'error') or contains(text(), 'Cannot') or contains(text(), 'Only')]"
#                         ))
#                     )
#                     error_text = error_elem.text.strip()
#                     print(f"Error for row {index}, client {client_id}: {error_text}")

#                     # Always cancel modal
#                     try:
#                         cancel_btn = WebDriverWait(driver, 3).until(
#                             EC.element_to_be_clickable((By.NAME, "owner_cancel"))
#                         )
#                         cancel_btn.click()
#                         time.sleep(1)
#                     except TimeoutException:
#                         print("Cancel button not found after error!")

#                     if "0% shares" in error_text:
#                         print(f"Shares exhausted for client {client_id}, skipping rest of owners.")
#                         break   # stop processing this client
#                     else:
#                         print(f"Validation error for client {client_id}, skipping row {index}.")
#                         pass

#                 except TimeoutException:
#                     # No error → assume success
#                     print(f"Row {index} for client {client_id} submitted successfully.")

#             except Exception as e:
#                 print(f"Error filling owner form for client {client_id}, row {index}: {e}")
#                 # Try cancel if form got stuck
#                 try:
#                     cancel_btn = WebDriverWait(driver, 2).until(
#                         EC.element_to_be_clickable((By.NAME, "owner_cancel"))
#                     )
#                     cancel_btn.click()
#                     print("Modal cancelled after exception during filling.")
#                     time.sleep(1)
#                 except TimeoutException:
#                     # continue
#                     print("Cancel button not found after exception during filling!")
#                 # continue

#     print("All owners processed for all clients.")

def click_cancel(driver, row_index):
    """
    Retry clicking the Cancel button multiple times.
    """
    for attempt in range(5):
        try:
            cancel_btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.NAME, "owner_cancel"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", cancel_btn)
            driver.execute_script("arguments[0].click();", cancel_btn)
            print(f"Modal cancelled for row {row_index}")
            return True
        except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
            time.sleep(1)
    print(f"Could not click Cancel for row {row_index}")
    return False

def fill_owner_forms(driver):
    df = pd.read_excel(r"owner200.xlsx")  # Modify path as needed
    try:
        tab = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Owner Details']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
    except TimeoutException:
        print("Owner Details tab not found!")

    for index, row in df.iterrows():

        try:
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
            )
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
            )
            button.click()
        except (ElementClickInterceptedException, TimeoutException) as e:
            print(f"Error clicking Create button: {e}")
            continue

        time.sleep(2)


        try:
            # Fill client name
            # driver.find_element(By.NAME, "first_name").send_keys(row["first_name"])
            # driver.find_element(By.NAME, "last_name").send_keys(row["last_name"])
            # driver.find_element(By.NAME, "share").send_keys(row["share"])
            # driver.find_element(By.NAME, "pan").send_keys(row["pan"])
            # driver.find_element(By.NAME, "aadhar").send_keys(row["aadhar"])
            # driver.find_element(By.NAME, "email").send_keys(row["email"])
            # driver.find_element(By.NAME, "username").send_keys(row["username"])
            # driver.find_element(By.NAME, "it_password").send_keys(row["it_password"])
            # driver.find_element(By.NAME, "mobile").send_keys(row["mobile"])
            # driver.find_element(By.NAME, "user_password").send_keys(row["user_password"])
            fields = [
                "first_name", "last_name", "share", "pan", "aadhar",
                "email", "username", "it_password", "mobile", "user_password"
            ]
            for field in fields:
                elem = driver.find_element(By.NAME, field)
                elem.clear()
                elem.send_keys(str(row[field]))


            isadmin = row["isadmin"]
        

            # Check if 'customer' is True, then click the checkbox
            isadmin_checkbox = driver.find_element(By.NAME, "isadmin")
            if isadmin:  # If customer is True
                if not isadmin_checkbox.is_selected():  # Check if it's not already selected
                    isadmin_checkbox.click()
            else:
                if isadmin_checkbox.is_selected():  # If it was selected, unselect it
                    isadmin_checkbox.click()

            wait = WebDriverWait(driver, 5)  # Waits up to 5 seconds
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]")))
            button.click()

            time.sleep(2)
            try:
                error_elem = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'Only 0% is left for assigning')]"
                    ))
                )
                if error_elem:
                    print(f"Shares exhausted message for row {index}: {error_elem.text}")
                    click_cancel(driver, index)
                    print("Stopping further processing due to 0% shares left.")
                    break  # Stop all processing
            except TimeoutException:
                # No share error → assume success
                print(f"Row {index} submitted successfully.")

    

           
            # for attempt in range(3):  # Retry up to 3 times
            #     try:
            #         error_message_elem = WebDriverWait(driver, 5).until(
            #             EC.visibility_of_element_located((
            #                 By.XPATH,
            #                 "//*[contains(text(), 'Only 0% is left for assigning')]"
            #             ))
            #         )

            #         if error_message_elem:
            #             print("Error detected:", error_message_elem.text)

            #             # Always re-find the cancel button just before clicking
            #             button = WebDriverWait(driver, 5).until(
            #                 EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Cancel']]"))
            #             )
            #             button.click()
            #             time.sleep(2)

            #             # Call the form function again after cancelling
            #             # bank.fill_bank_forms(driver)
            #             shares_exhausted = True
            #             break

            #     except (TimeoutException, StaleElementReferenceException):
            #         # If error element is not found or gets stale, we just continue.
            #         pass

            time.sleep(2)  # Small pause before processing the next owner. 

        except Exception as e:
            print(f"Error filling owner form for row {index}: {e}")
            continue
    time.sleep(5)


if __name__ == "__main__":
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("vaishnavi")
    driver.find_element(By.NAME, "login").click()
    time.sleep(2)

    driver.find_element(By.ID, "long-button").click()
    view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    view_button.click()
    time.sleep(2)

    fill_owner_forms(driver)
    time.sleep(2)
    driver.quit()
    print("Owner form submission done.")
