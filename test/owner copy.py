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
import bank
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# def fill_owner_forms(driver):
#     df = pd.read_excel(r"owner2.xlsx")  # Modify path as needed

#     for index, row in df.iterrows():

#         try:
#             tab = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.XPATH, "//*[text()='Owner Details']"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", tab)
#             WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
#             driver.execute_script("arguments[0].click();", tab)
#         except TimeoutException:
#             print("Owner Details tab not found!")



#         try:
#             WebDriverWait(driver, 5).until(
#                 EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
#             )
#             button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
#             )
#             button.click()
#         except (ElementClickInterceptedException, TimeoutException) as e:
#             print(f"Error clicking Create button: {e}")
#             continue

#         time.sleep(2)


#         try:
#             # Fill client name
#             driver.find_element(By.NAME, "first_name").send_keys(row["first_name"])
#             driver.find_element(By.NAME, "last_name").send_keys(row["last_name"])
#             driver.find_element(By.NAME, "share").send_keys(row["share"])
#             driver.find_element(By.NAME, "pan").send_keys(row["pan"])
#             driver.find_element(By.NAME, "aadhar").send_keys(row["aadhar"])
#             driver.find_element(By.NAME, "email").send_keys(row["email"])
#             driver.find_element(By.NAME, "username").send_keys(row["username"])
#             driver.find_element(By.NAME, "it_password").send_keys(row["it_password"])
#             driver.find_element(By.NAME, "mobile").send_keys(row["mobile"])
#             driver.find_element(By.NAME, "user_password").send_keys(row["user_password"])

#             isadmin = row["isadmin"]
        

#             # Check if 'customer' is True, then click the checkbox
#             isadmin_checkbox = driver.find_element(By.NAME, "isadmin")
#             if isadmin:  # If customer is True
#                 if not isadmin_checkbox.is_selected():  # Check if it's not already selected
#                     isadmin_checkbox.click()
#             else:
#                 if isadmin_checkbox.is_selected():  # If it was selected, unselect it
#                     isadmin_checkbox.click()

#             wait = WebDriverWait(driver, 5)  # Waits up to 5 seconds
#             button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]")))
#             button.click()

#             time.sleep(2)
           
#             for attempt in range(3):  # Retry up to 3 times
#                 try:
#                     error_message_elem = WebDriverWait(driver, 5).until(
#                         EC.visibility_of_element_located((
#                             By.XPATH,
#                             "//*[contains(text(), 'Only 0% is left for assigning')]"
#                         ))
#                     )

#                     if error_message_elem:
#                         print("Error detected:", error_message_elem.text)

#                         # Always re-find the cancel button just before clicking
#                         button = WebDriverWait(driver, 5).until(
#                             EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Cancel']]"))
#                         )
#                         button.click()
#                         time.sleep(2)

#                         # Call the form function again after cancelling
#                         # bank.fill_bank_forms(driver)
#                         shares_exhausted = True
#                         break

#                 except (TimeoutException, StaleElementReferenceException):
#                     # If error element is not found or gets stale, we just continue.
#                     pass

#             time.sleep(2)  # Small pause before processing the next owner. 

#         except Exception as e:
#             print(f"Error filling owner form for row {index}: {e}")
#             continue
#     time.sleep(5)


# def fill_owner_forms(driver):
#     df = pd.read_excel(r"owner500.xlsx")  # Modify path as needed

#     # df["client_id"] = df["client_id"].astype(int)

#     for index, row in df.iterrows():
#         # client_id = row["client_id"]  # Column in Excel 
#         # print(f"Processing client_id: {client_id}")

#         client_id = row["client_id"]
#         if pd.isna(client_id):
#             print(f"Skipping row {index} because client_id is empty")
#             continue

#         client_id = int(client_id)  # safely convert 1.0 → 1
#         print(f"Processing client_id: {client_id}")

#         try:
#             # Navigate to the client's Owner Details page
#             driver.get(f"http://localhost:5173/clientDetails/{client_id}")
#             # driver.get(f"http://localhost:5173/api/create-owner/{client_id}")
#             time.sleep(2)

#             tab = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.XPATH, "//*[text()='Owner Details']"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", tab)
#             WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
#             driver.execute_script("arguments[0].click();", tab)

#         except TimeoutException:
#             print(f"Owner Details tab not found for client {client_id}!")
#             continue

#         try:
#             WebDriverWait(driver, 5).until(
#                 EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
#             )
#             button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
#             )
#             button.click()
#         except (ElementClickInterceptedException, TimeoutException) as e:
#             print(f"Error clicking Create button for client {client_id}: {e}")
#             continue

#         time.sleep(2)

#         try:
#             # Fill owner details
#             driver.find_element(By.NAME, "first_name").send_keys(row["first_name"])
#             driver.find_element(By.NAME, "last_name").send_keys(row["last_name"])
#             driver.find_element(By.NAME, "share").send_keys(row["share"])
#             driver.find_element(By.NAME, "pan").send_keys(row["pan"])
#             driver.find_element(By.NAME, "aadhar").send_keys(row["aadhar"])
#             driver.find_element(By.NAME, "email").send_keys(row["email"])
#             driver.find_element(By.NAME, "username").send_keys(row["username"])
#             driver.find_element(By.NAME, "it_password").send_keys(row["it_password"])
#             driver.find_element(By.NAME, "mobile").send_keys(row["mobile"])
#             driver.find_element(By.NAME, "user_password").send_keys(row["user_password"])

#             isadmin = row["isadmin"]
#             isadmin_checkbox = driver.find_element(By.NAME, "isadmin")
#             if isadmin and not isadmin_checkbox.is_selected():
#                 isadmin_checkbox.click()
#             elif not isadmin and isadmin_checkbox.is_selected():
#                 isadmin_checkbox.click()

#             button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
#             )
#             button.click()

#             time.sleep(2)

#             # Handle share limit error
#             for attempt in range(3):
#                 try:
#                     error_message_elem = WebDriverWait(driver, 5).until(
#                         EC.visibility_of_element_located((
#                             By.XPATH,
#                             "//*[contains(text(), 'Only 0% is left for assigning')]"
#                         ))
#                     )
#                     if error_message_elem:
#                         print("Error detected:", error_message_elem.text)
#                         cancel_button = WebDriverWait(driver, 5).until(
#                             EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Cancel']]"))
#                         )
#                         cancel_button.click()
#                         time.sleep(2)
#                         break
#                 except (TimeoutException, StaleElementReferenceException):
#                     pass

#             time.sleep(2)

#         except Exception as e:
#             print(f"Error filling owner form for client {client_id}, row {index}: {e}")
#             continue

#     time.sleep(5)


def fill_owner_forms(driver):
    df = pd.read_excel(r"owner500.xlsx")  # Modify path as needed

    # Ensure client_id is valid integer
    df = df[df["client_id"].notna()]  # Skip rows with NaN
    df["client_id"] = df["client_id"].astype(int)

    # Group by client_id
    grouped = df.groupby("client_id")

    for client_id, group in grouped:
        print(f"Processing client_id: {client_id}")

        try:
            # Navigate to the client's Owner Details page once per client
            driver.get(f"http://localhost:5173/clientDetails/{client_id}")
            time.sleep(2)

            tab = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Owner Details']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", tab)
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable(tab))
            driver.execute_script("arguments[0].click();", tab)

        except TimeoutException:
            print(f"Owner Details tab not found for client {client_id}!")
            continue

        for index, row in group.iterrows():
            try:
                WebDriverWait(driver, 2).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
                )
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
                )
                button.click()
            except (ElementClickInterceptedException, TimeoutException) as e:
                print(f"Error clicking Create button for client {client_id}, row {index}: {e}")
                continue

            # time.sleep(1)

            try:
                # Fill owner details
                driver.find_element(By.NAME, "first_name").send_keys(row["first_name"])
                driver.find_element(By.NAME, "last_name").send_keys(row["last_name"])
                driver.find_element(By.NAME, "share").send_keys(row["share"])
                driver.find_element(By.NAME, "pan").send_keys(row["pan"])
                driver.find_element(By.NAME, "aadhar").send_keys(row["aadhar"])
                driver.find_element(By.NAME, "email").send_keys(row["email"])
                driver.find_element(By.NAME, "username").send_keys(row["username"])
                driver.find_element(By.NAME, "it_password").send_keys(row["it_password"])
                driver.find_element(By.NAME, "mobile").send_keys(row["mobile"])
                driver.find_element(By.NAME, "user_password").send_keys(row["user_password"])

                isadmin = row["isadmin"]
                isadmin_checkbox = driver.find_element(By.NAME, "isadmin")
                if isadmin and not isadmin_checkbox.is_selected():
                    isadmin_checkbox.click()
                elif not isadmin and isadmin_checkbox.is_selected():
                    isadmin_checkbox.click()

                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
                )
                button.click()
                # time.sleep(1)

                # Handle share limit error
                for attempt in range(3):
                    try:
                        error_elem = WebDriverWait(driver, 3).until(
                            EC.visibility_of_element_located((
                                By.XPATH,
                                "//*[contains(text(), 'error') or contains(text(), 'Cannot') or contains(text(), 'Only')]"
                            ))
                        )
                        error_text = error_elem.text.strip()
                        print(f"Error for row {index}, client {client_id}: {error_text}")

                        cancel_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.NAME, "owner_cancel"))
                        )
                        cancel_btn.click()
                        time.sleep(1)

                        # --- Decision logic ---
                        if "0% shares" in error_text or "Cannot create owner because 0% shares" in error_text:
                            print(f"Shares exhausted for client {client_id}, moving to next client...")
                            break   # exit current client loop, go to next client
                        else:
                            print(f"Validation error for client {client_id}, skipping this row only...")
                            continue  # skip row but stay in same client

                    except TimeoutException:
                        # No error appeared → move normally
                        pass

                # time.sleep(1)

            except Exception as e:
                print(f"Error filling owner form for client {client_id}, row {index}: {e}")
                continue

    print("All owners processed for all clients.")



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

    

