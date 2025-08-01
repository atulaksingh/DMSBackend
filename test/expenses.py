import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options

def fill_expenses_forms(driver):
    options = Options()
    options.add_experimental_option("detach", True)  

    df = pd.read_excel(r"exp2.xlsx")  
    print(df.columns)
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Expenses')]")
    button.click()

    # Convert date_of_incorporation to MM-DD-YYYY format 
    df.columns = df.columns.str.strip() 
    df["month"] = pd.to_datetime(df["month"]).dt.strftime("%m-%d-%Y")
    df["invoice_date"] = pd.to_datetime(df["invoice_date"]).dt.strftime("%m-%d-%Y")

    for index, row in df.iterrows():
        print(list(df.columns))  # Check exact column names

        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]").click()
        time.sleep(1)

        # contact_field = driver.find_element(By.NAME, "contact")
        
        # Office Location
        location = row["location"]
        autocomplete_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "location-select"))
        )
        autocomplete_input.clear()
        autocomplete_input.send_keys(location[:10])  
        time.sleep(1)

        try:
            # Check if dropdown options appear
            dropdown_options = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
            )
            available_countries = [opt.text.strip() for opt in dropdown_options]
            print("Dropdown options:", available_countries)

            for option in dropdown_options:
                if option.text.strip().endswith(location):  # Match exact country
                    ActionChains(driver).move_to_element(option).click().perform()
                    time.sleep(1)
                    break
                else:
                    print(f"Country '{location}' not found in dropdown!")

        except Exception:
            print("No dropdown options available for location, proceeding with direct input.")
            # driver.find_element(By.ID, "location-select").send_keys(row['location'])
            # time.sleep(2)

        # Fill other fields
            driver.find_element(By.XPATH, "//input[@name='contact' and @type='number']").send_keys(row['contact'])
            # if len(contact_field) > 1:
            #     contact_field[0].send_keys(row['contact'])
            time.sleep(1)

            driver.find_element(By.NAME, "address").send_keys(row['address'])
            time.sleep(1)

            driver.find_element(By.NAME, "city").send_keys(row['city'])
            time.sleep(1)

            driver.find_element(By.NAME, "state").send_keys(row['state'])
            time.sleep(1)

            driver.find_element(By.NAME, "country").send_keys(row['country'])
            time.sleep(1)

            # Always use dropdown for Branch Selection
            branch = row["branch"].strip()
            autocomplete_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "branch-select"))
            )
            autocomplete_input.click()
            time.sleep(1)

            dropdown_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
            )

            available_branch = [opt.text.strip() for opt in dropdown_options]
            print("Dropdown options:", available_branch)
            time.sleep(2)

            for option in dropdown_options:
                if option.text.strip().endswith(branch):  # Match exact branch
                    ActionChains(driver).move_to_element(option).click().perform()
                    break
            else:
                print(f"Branch '{branch}' not found in dropdown!")

           
        # Fill Invoice Details
        driver.find_element(By.NAME, "invoice_no").send_keys(row['invoice_no'])
        time.sleep(1)

        file_input = driver.find_element(By.NAME, 'attach_invoice')
        file_input.send_keys(row["attach_invoice"])
        time.sleep(1)

        file_input = driver.find_element(By.NAME, 'attach_e_way_bill')
        file_input.send_keys(row["eway_bill"])
        time.sleep(1)

        date_input = driver.find_element(By.NAME, "month")
        date_input.click()
        time.sleep(1)  # Allow calendar to open
        date_input.send_keys(Keys.CONTROL + "a")  # Select existing date (if any)
        date_input.send_keys(Keys.BACKSPACE)  # Clear existing date
        date_input.send_keys(row["month"])  # Enter date in MM-DD-YYYY format
        date_input.send_keys(Keys.ENTER)  # Confirm selection 
        time.sleep(1)

        date_input = driver.find_element(By.NAME, "invoice_date")
        date_input.click()
        time.sleep(1) 
        date_input.send_keys(Keys.CONTROL + "a") 
        date_input.send_keys(Keys.BACKSPACE)  
        date_input.send_keys(row["invoice_date"])  
        date_input.send_keys(Keys.ENTER) 
        time.sleep(2)

        # Fill Customer and Vendor Details
        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Customer And Vendor Details')]")
        button.click()
        time.sleep(2)
        gst = row["gst_no"]
        autocomplete_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "gst-no-autocomplete"))
        )
        autocomplete_input.clear()
        autocomplete_input.send_keys(gst[:20])
        time.sleep(1)

        try:
            dropdown_options = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]")),
            )
            available_gst = [opt.text.strip() for opt in dropdown_options]
            print("Dropdown options:", available_gst)
            time.sleep(2)

            for option in dropdown_options:
                if option.text.strip().endswith(gst):
                    ActionChains(driver).move_to_element(option).click().perform()
                    time.sleep(2)
                    break
                else:
                    print(f"GST '{gst}' not found in dropdown! ")

        except Exception :

            print("No dropdown options available for location, proceeding with direct input.")

            driver.find_element(By.NAME, "name").send_keys(row['name'])
            time.sleep(1)

            driver.find_element(By.NAME, "pan").send_keys(row['pan'])
            time.sleep(1)

            driver.find_element(By.NAME, "vendor_address").send_keys(row['address'])
            time.sleep(1)

            driver.find_element(By.NAME, "email").send_keys(row['email'])
            time.sleep(1)

            # driver.find_element(By.XPATH, "//input[@name='contact' and @type='text']").send_keys(row['contact_no'])        
            # time.sleep(1)
            driver.find_elements(By.XPATH, '//input[@placeholder="Contact No"]')[1].send_keys(row['contact_no'])
            time.sleep(1)

            customer = row["customer"]
            vendor = row["vendor"]

            # Check if 'customer' is True, then click the checkbox
            customer_checkbox = driver.find_element(By.NAME, "customer")
            if customer:  # If customer is True
                if not customer_checkbox.is_selected():  # Check if it's not already selected
                    customer_checkbox.click()
            else:
                if customer_checkbox.is_selected():  # If it was selected, unselect it
                    customer_checkbox.click()

            # Check if 'vendor' is True, then click the checkbox
            vendor_checkbox = driver.find_element(By.NAME, "vendor")
            if vendor:  # If vendor is True
                if not vendor_checkbox.is_selected():
                    vendor_checkbox.click()
            else:
                if vendor_checkbox.is_selected():
                    vendor_checkbox.click()

            time.sleep(2)

        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Product Details')]")
        button.click()
        time.sleep(2)

        
        product = row["product"]
        autocomplete_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "product-autocomplete-0"))
        )
        autocomplete_input.clear()
        autocomplete_input.send_keys(product[:3])
        time.sleep(1)

        try:
            dropdown_options = WebDriverWait(driver, 2).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
            )
            available_gst = [opt.text.strip() for opt in dropdown_options]
            print("Dropdown options:", available_gst)

            for option in dropdown_options:
                if option.text.strip().endswith(product):  # Match exact country
                    ActionChains(driver).move_to_element(option).click().perform()
                    time.sleep(2)
                    driver.find_element(By.ID, "description-0").send_keys(row['description'])
                    time.sleep(2)
                    driver.find_element(By.ID, "unit-0").send_keys(row['unit'])
                    time.sleep(2)
                    driver.find_element(By.ID, "rate-0").send_keys(row['rate'])
                    time.sleep(2)
                    break
                else:
                    print(f"Country '{product}' not found in dropdown!")
                    # driver.find_element(By.XPATH, "//input[contains(@class, 'MuiInputBase-input')]").send_keys(row['description'])
                    # time.sleep(10)


        except Exception as e:
            print("No dropdown options available or click failed:", str(e))
            autocomplete_input.clear()
            autocomplete_input.send_keys(product[3:])

            driver.find_element(By.ID, "description-0").send_keys(row['description'])
            time.sleep(2)
            driver.find_element(By.ID, "hsn_code-0").send_keys(row['hsn_code'])
            time.sleep(2)
            driver.find_element(By.ID, "unit-0").send_keys(row['unit'])
            time.sleep(2)
            driver.find_element(By.ID, "rate-0").send_keys(row['rate'])
            time.sleep(2)
            driver.find_element(By.ID, "gst_rate-0").send_keys(row['gst_rate'])
            time.sleep(2)
        
        driver.find_element(By.NAME, "add-product").click()

        product = row["product2"]
        autocomplete_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "product-autocomplete-1"))
        )
        autocomplete_input.clear()
        autocomplete_input.send_keys(product[:3])
        time.sleep(1)

        try:
            dropdown_options = WebDriverWait(driver, 2).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'MuiAutocomplete-option')]"))
            )
            available_gst = [opt.text.strip() for opt in dropdown_options]
            print("Dropdown options:", available_gst)

            for option in dropdown_options:
                if option.text.strip().endswith(product):  # Match exact country
                    ActionChains(driver).move_to_element(option).click().perform()
                    time.sleep(2)
                    driver.find_element(By.ID, "description-1").send_keys(row['description2'])
                    time.sleep(2)
                    driver.find_element(By.ID, "unit-1").send_keys(row['unit2'])
                    time.sleep(2)
                    driver.find_element(By.ID, "rate-1").send_keys(row['rate2'])
                    time.sleep(2)
                    break
                else:
                    print(f"Country '{product}' not found in dropdown!")
                    # driver.find_element(By.XPATH, "//input[contains(@class, 'MuiInputBase-input')]").send_keys(row['description'])
                    # time.sleep(10)


        except Exception as e:
            print("No dropdown options available or click failed:", str(e))
            autocomplete_input.clear()
            autocomplete_input.send_keys(product[3:])

            driver.find_element(By.ID, "description-1").send_keys(row['description2'])
            time.sleep(2)
            driver.find_element(By.ID, "hsn_code-1").send_keys(row['hsn_code2'])
            time.sleep(2)
            driver.find_element(By.ID, "unit-1").send_keys(row['unit2'])
            time.sleep(2)
            driver.find_element(By.ID, "rate-1").send_keys(row['rate2'])
            time.sleep(2)
            driver.find_element(By.ID, "gst_rate-1").send_keys(row['gst_rate2'])
            time.sleep(2)

        # Select Invoice Type
        invoice_type = row["invoice_type"].strip()

        # Wait for the select dropdown to be present
        dropdown_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "invoice_type"))
        )

        # Convert the element to a Select object
        select = Select(dropdown_element)

        # Get available options
        dropdown_options = [opt.text.strip() for opt in select.options]
        print("Dropdown options:", dropdown_options)
        time.sleep(2)

        # Select the matching option
        if invoice_type in dropdown_options:
            select.select_by_visible_text(invoice_type)
            print(f"Selected Invoice Type: {invoice_type}")
            time.sleep(2)
        else:
            print(f"Invoice Type '{invoice_type}' not found in dropdown!")

        # Select TDS/ TCS Type
        invoice_type = row["select_tds_tcs"].strip()

        # Wait for the select dropdown to be present
        dropdown_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "option"))
        )

        # Convert the element to a Select object
        select = Select(dropdown_element)

        # Get available options
        dropdown_options = [opt.text.strip() for opt in select.options]
        print("Dropdown options:", dropdown_options)
        time.sleep(2)

        # Select the matching option
        if invoice_type in dropdown_options:
            select.select_by_visible_text(invoice_type)
            print(f"Selected Invoice Type: {invoice_type}")
            time.sleep(2)
        else:
            print(f"Invoice Type '{invoice_type}' not found in dropdown!")

        driver.find_element(By.NAME, "tds_tcs_rate").send_keys(row['enter'])
        time.sleep(5)

        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
        )
        button.click()
        time.sleep(1)


if __name__ == "__main__":

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    driver.find_element(By.ID, "long-button").click()
    view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
    view_button.click()
    time.sleep(2)

    fill_expenses_forms(driver)
    time.sleep(1)
    time.sleep(1)
    driver.quit()
    print("Expenses form submission done.")

    
