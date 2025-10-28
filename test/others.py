import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
# import officelocation  # optional if you want to call it later
import customeruser

def fill_others_forms(driver):
    # Load the Excel data
    df = pd.read_excel(r"others200.xlsx")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Click on 'Documents' tab
    try:
        time.sleep(10)
        tab = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Documents']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(tab))
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(2)
    except TimeoutException:
        print("Documents tab not found!")
    

    for index, row in df.iterrows():
        print(df.columns.tolist())


        button = driver.find_element(By.XPATH, "//button[normalize-space()='Others']")
        driver.execute_script("arguments[0].click();", button)


        try:
            # Wait for backdrop to disappear
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "MuiBackdrop-root"))
            )

            create_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Create')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", create_button)
            create_button.click()


        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"Error clicking Create button: {e}")
            continue

        time.sleep(2)  # wait for form to appear

        try:

            # Month
            month_field = driver.find_element(By.NAME, "month")
            month_field.clear()
            month_field.send_keys(row["month"])                     
            # driver.find_element(By.NAME, "month").send_keys(row["month"])

            login_year = str(row["login_year"])  # ensure it's a string
            dropdown = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'css-13cymwt-control')]"))
            )
            dropdown.click()
            time.sleep(0.5)  # let menu render
            option_xpath = f"//div[@role='option' and normalize-space(text())='{login_year}']"
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            driver.execute_script("arguments[0].click();", option)  # JS click is safer
            time.sleep(0.5)


            # Nature of Report
            text_field = driver.find_element(By.NAME, "text")
            text_field.clear()
            text_field.send_keys(row["nature"])
            # driver.find_element(By.NAME, "text").send_keys(row["nature"])

            # Computation file upload handling
            file_input = driver.find_element(By.NAME, 'files')
            file_input.clear()
            file_input.send_keys(row["file1"])
            file_input.send_keys(row["file2"])

            # Click Confirm button
            # Click Confirm button (best way: by name)
            confirm_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.NAME, "others_submit"))
            )
            driver.execute_script("arguments[0].click();", confirm_button)

            try:
                error_elem = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//*[contains(text(), 'required') or contains(text(), 'one file') or contains(text(), 'must be')]"
                    ))
                )
                error_text = error_elem.text.strip()
                print(f"Error for row {index}, client: {error_text}")               
                # Always cancel modal
                try:
                    cancel_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.NAME, "others_cancel"))
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
            try:
                cancel_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.NAME, "others_cancel"))
                )
                cancel_btn.click()
                print("Modal cancelled after exception during filling.")
                time.sleep(1)
            except TimeoutException:
                # continue
                print("Cancel button not found after exception during filling!")
            # continue

        time.sleep(2)  # small pause before next user

    # customeruser.fill_customeruser_forms(driver)

if __name__ == "__main__":
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    # Login
    driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("vaishnavi")
    driver.find_element(By.NAME, "login").click()
    time.sleep(3)

    # Open menu
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

    fill_others_forms(driver)

    time.sleep(3)
    driver.quit()
    print("User form submission done.")
