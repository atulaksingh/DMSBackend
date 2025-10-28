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


def fill_branchdoc_forms(driver):
    # Load the Excel data
    
    df = pd.read_excel(r"branchdoc500.xlsx")
    df = df.iloc[500:] 

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
        
        time.sleep(3)
        try:
            print('AAAAAAAA')
            create_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
            )
            create_btn.click()
            time.sleep(2)

            # Fill dropdown
            dropdown = driver.find_element(By.NAME, "document_type")
            # dropdown.clear()
            dropdown.click()
            document_type = row["Document Type"].strip()
            option_xpath = f"//li[normalize-space(text())='{document_type}']"
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            option.click()
            print('BBBB')

            # Fill inputs
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

            # Upload files
            file_input = driver.find_element(By.NAME, 'files')
            file_input.clear()
            if pd.notna(row["File1"]):
                file_input.send_keys(row["File1"])
            if pd.notna(row["File2"]):
                file_input.send_keys(row["File2"])

            # Confirm
            # confirm_btn = webdriver (driver, 5).until(confirm_btn = we)
            confirm_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
            )
            confirm_btn.click()

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
                        EC.element_to_be_clickable((By.NAME, "branchdoc_cancel"))
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
                    EC.element_to_be_clickable((By.NAME, "branchdoc_cancel"))
                )
                cancel_btn.click()
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[text()='ClientDetails']"))
                )
                element.click()
                time.sleep(2)

                print("Modal cancelled after exception during filling.")
                time.sleep(1)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue

        time.sleep(2)

    # Call office location fill if needed
    officelocation.fill_officeloc_forms(driver)

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

    fill_branchdoc_forms(driver)
    time.sleep(3)
    driver.quit()
    print("Purchase form submission done.")


