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
from selenium.common.exceptions import TimeoutException

def clear_and_fill_autocomplete(driver, field_id, value):
    """
    Clear previous value from a Material-UI autocomplete and select a new value.
    """
    try:
        input_field = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, field_id))
        )
        input_field.click()
        input_field.send_keys(Keys.CONTROL + "a")  # Select all
        input_field.send_keys(Keys.DELETE)         # Delete
        time.sleep(0.5)

        input_field.send_keys(value[:10])
        time.sleep(1)

        options = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class,'MuiAutocomplete-option')]"))
        )

        for option in options:
            if option.text.strip().endswith(value):
                ActionChains(driver).move_to_element(option).click().perform()
                time.sleep(1)
                break
        else:
            print(f"Value '{value}' not found in {field_id} dropdown!")

    except Exception as e:
        print(f"Error in {field_id}: {e}")


def fill_officeloc_forms(driver):
    # Load the Excel data
    
    df = pd.read_excel(r"officelocation500.xlsx")
    df = df.iloc[311:] 

    for index, row in df.iterrows():
        try:
            time.sleep(10)
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
        
        time.sleep(2)
        try:
            button = driver.find_element(By.XPATH, "//button[contains(text(), 'Office Location')]")
            button.click()

            create_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
            )
            create_btn.click()
            time.sleep(2)

            # Fill in the form fields
            location_field = driver.find_element(By.NAME, "location")
            location_field.clear()
            location_field.send_keys(row["location"])

            contact_field = driver.find_element(By.NAME, "contact")
            contact_field.clear()
            contact_field.send_keys(str(row["contact"]))
           
            for field_name in ["location", "contact", "address"]:
                try:
                    field = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.NAME, field_name))
                    )
                    field.clear()
                    field.send_keys(str(row[field_name]))
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error filling {field_name}: {e}")

            # Fill autocomplete fields
            clear_and_fill_autocomplete(driver, "country-select", row["country"])
            clear_and_fill_autocomplete(driver, "state-select", row["state"])
            clear_and_fill_autocomplete(driver, "city-select", row["city"])

            button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            button.click()

            try:
                error_elem = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'required')  or contains(text(), 'must be') or contains(text(), 'can only contain')]"
                    ))
                )
                error_text = error_elem.text.strip()
                print(f"Error for row {index}, client: {error_text}")               
                # Always cancel modal
                try:
                    cancel_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.NAME, "clientuser_cancel"))
                    )
                    cancel_btn.click()
                    time.sleep(1)
                except TimeoutException:
                    print("Cancel button not found after error!")

            except TimeoutException:
                # No error → assume success
                print(f"Row {index} for client submitted successfully.")


            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='ClientDetails']"))
            )
            element.click()
            time.sleep(2)


            print(f"✅ Added BranchDoc row {index+1} for {branch_name}")

        except Exception as e:
            print(f"❌ Error filling doc row {index+1}: {e}")
            try:
                cancel_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.NAME, "officelocation_cancel"))
                )
                cancel_btn.click()
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[text()='ClientDetails']"))
                )
                element.click()
                print("Modal cancelled after exception during filling.")
                time.sleep(2)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue

        time.sleep(2)

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

    fill_officeloc_forms(driver)
    time.sleep(3)
    driver.quit()
    print("Purchase form submission done.")

# # Wait for a few seconds before quitting
# time.sleep(15)
# driver.quit()
# print("Done")
