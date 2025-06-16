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



# df = pd.read_excel(r"owner_data.xlsx")  # Modify path as needed

# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
# driver.get("http://localhost:5173/")
# time.sleep(2)

# driver.find_element(By.ID, "long-button").click()

# view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
# view_button.click()

# time.sleep(5)

def fill_owner_forms(driver):
    df = pd.read_excel(r"owner2.xlsx")  # Modify path as needed

    for index, row in df.iterrows():

        # try :
        #     button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")

        #     # Check if the button is obscured
        #     if button.is_displayed() and button.is_enabled():
        #         button.click()
        #     else:
        #         print("Button is not clickable due to being obscured or disabled")
        # except Exception as e:
        #     print(f"Error clicking Create button: {e}")
        #     continue
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
            )
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
            )
            button.click()
        except (ElementClickInterceptedException, TimeoutException) as e:
            print(f"Error clicking Create button: {e}")
            continue

        time.sleep(2)


        try:
            # Fill client name
            driver.find_element(By.NAME, "owner_name").send_keys(row["owner_name"])
            driver.find_element(By.NAME, "share").send_keys(row["share"])
            driver.find_element(By.NAME, "pan").send_keys(row["pan"])
            driver.find_element(By.NAME, "aadhar").send_keys(row["aadhar"])
            driver.find_element(By.NAME, "email").send_keys(row["email"])
            driver.find_element(By.NAME, "username").send_keys(row["username"])
            driver.find_element(By.NAME, "it_password").send_keys(row["it_password"])
            driver.find_element(By.NAME, "mobile").send_keys(row["mobile"])

            isadmin = row["isadmin"]
        

            # Check if 'customer' is True, then click the checkbox
            isadmin_checkbox = driver.find_element(By.NAME, "isadmin")
            if isadmin:  # If customer is True
                if not isadmin_checkbox.is_selected():  # Check if it's not already selected
                    isadmin_checkbox.click()
            else:
                if isadmin_checkbox.is_selected():  # If it was selected, unselect it
                    isadmin_checkbox.click()


            # isadmin_value = row["isadmin"]

            # if isadmin_value == "TRUE":
            #     driver.find_element(By.NAME, "isadmin").click()
            # else:
            #     driver.find_element(By.NAME, "isadmin")

            # driver.find_element(By.NAME, "owner-confirm").click()
            wait = WebDriverWait(driver, 10)  # Waits up to 10 seconds
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]")))
            button.click()

            time.sleep(2)
            # try:
            #     error_message_elem = WebDriverWait(driver, 5).until(
            #         EC.visibility_of_element_located((
            #             By.XPATH,
            #             "//*[contains(text(), 'Only 0% is left for assigning')]"
            #         ))
            #     )
            #     if error_message_elem:
            #         # If error is detected, print and set flag.
            #         print("Error detected:", error_message_elem.text)
            #         button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Cancel']]")))
            #         button.click()
            #         time.sleep(2)
            #         bank.fill_bank_forms(driver)
            #         shares_exhausted = True
            #         break  # Stop processing further owners.
            # except Exception:
            #     # If the error element is not found within 5 seconds, assume no error occurred.
            #     pass
            #     bank.fill_bank_forms(driver)
            for attempt in range(3):  # Retry up to 3 times
                try:
                    error_message_elem = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((
                            By.XPATH,
                            "//*[contains(text(), 'Only 0% is left for assigning')]"
                        ))
                    )

                    if error_message_elem:
                        print("Error detected:", error_message_elem.text)

                        # Always re-find the cancel button just before clicking
                        button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Cancel']]"))
                        )
                        button.click()
                        time.sleep(2)

                        # Call the form function again after cancelling
                        # bank.fill_bank_forms(driver)
                        shares_exhausted = True
                        break

                except (TimeoutException, StaleElementReferenceException):
                    # If error element is not found or gets stale, we just continue.
                    pass

                # Try to fill the form anyway if no error occurred
                # try:
                #     bank.fill_bank_forms(driver)
                # except StaleElementReferenceException:
                #     print("Retrying due to stale reference in form...")
                #     continue
                # break  # Break the loop if form was filled successfully

            time.sleep(2)  # Small pause before processing the next owner. 

        except Exception as e:
            print(f"Error filling owner form for row {index}: {e}")
            continue
    time.sleep(5)

if __name__ == "__main__":

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.ID, "long-button").click()
    view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    view_button.click()
    time.sleep(2)

    fill_owner_forms(driver)
    time.sleep(8)
    driver.quit()
    print("Owner form submission done.")

    

