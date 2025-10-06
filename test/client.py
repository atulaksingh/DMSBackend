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
from selenium.common.exceptions import TimeoutException
# Import your tab-handling modules
import owner
import bank
import branch
import user
import branchdoc
import companydoc
import taxaudit
import air
import sft
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


# Setup the WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("http://localhost:5173/")
time.sleep(2)

# Login
driver.find_element(By.NAME, "username").send_keys("vaishnavitalari.v@gmail.com")
driver.find_element(By.NAME, "password").send_keys("vaishnavi")
driver.find_element(By.NAME, "login").click()
time.sleep(5)

# Read data from Excel file
df = pd.read_excel(r"client10.xlsx")  

# Convert date_of_incorporation to MM-DD-YYYY format
df["date_of_incorporation"] = pd.to_datetime(df["date_of_incorporation"]).dt.strftime("%m-%d-%Y")

# LOOP for each client
for index, row in df.iterrows():
    client_name = row["client_name"]
    print(f"\n🚀 Creating client {index+1}: {client_name}")

    # ---- Create Client ----
    driver.find_element(By.CSS_SELECTOR, "a[href='/client'] button").click()
    
    driver.find_element(By.NAME, "client_name").send_keys(row["client_name"])

    # Select entity type
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='entity_type']"))
    )
    dropdown_button.click()
    dropdown_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']"))
    )
    if dropdown_options:
        random.choice(dropdown_options).click()

    # Date of incorporation
    date_input = driver.find_element(By.NAME, "date_of_incorporation")
    date_input.click()
    date_input.send_keys(Keys.CONTROL + "a")
    date_input.send_keys(Keys.BACKSPACE)
    date_input.send_keys(row["date_of_incorporation"])
    date_input.send_keys(Keys.ENTER)

    # Other fields
    driver.find_element(By.NAME, "contact_person").send_keys(row["contact_person"])
    driver.find_element(By.NAME, "designation").send_keys(row["designation"])
    driver.find_element(By.NAME, "email").send_keys(row["email"])
    driver.find_element(By.NAME, "contact_no_1").send_keys(str(row["contact_no_1"]))
    driver.find_element(By.NAME, "contact_no_2").send_keys(str(row["contact_no_2"]))
    driver.find_element(By.NAME, "business_detail").send_keys(row["business_detail"])

    # Status dropdown
    dropdown_button_status = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='status']"))
    )
    dropdown_button_status.click()
    dropdown_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']"))
    )
    if dropdown_options:
        random.choice(dropdown_options).click()

    label = driver.find_element(By.XPATH, "//label[contains(text(), 'Select PDF/image file.')]")

    # Click it
    label.click()
    wait = WebDriverWait(driver, 10)

    # for index, row in df.iterrows():
    document_type = row["document_type"]  # e.g. PAN, TAN

    print(f"Selecting: {document_type}")

    dropdown = wait.until(EC.element_to_be_clickable((By.NAME, "file_name")))
    dropdown.click()

    option_xpath = f"//ul[@role='listbox']//li[normalize-space(text())='{document_type}']"
    option = wait.until(EC.presence_of_element_located((By.XPATH, option_xpath)))
    driver.execute_script("arguments[0].click();", option)


    driver.find_element(By.NAME, "login").send_keys(row["login"])
    driver.find_element(By.NAME, "password").send_keys(row["password"])
    driver.find_element(By.NAME, "remark").send_keys(row["remark"])

    # File upload handling
    file_input = driver.find_element(By.NAME, 'file')
    file_input.send_keys(row["file1"])
    file_input.send_keys(row["file2"])
    file_input.send_keys(row["file3"])

    # Submit the form
    driver.find_element(By.NAME, "upload").click()

    # Submit the form
    driver.find_element(By.NAME, "create-btn").click()
    time.sleep(3)

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

   # ---- Fill ALL Tabs for this client ----
    owner.fill_owner_forms(driver)
    bank.fill_bank_forms(driver)
    branch.fill_branch_forms(driver)
    branchdoc.fill_branchdoc_forms(driver)
    user.fill_clientuser_forms(driver)
    companydoc.fill_companydoc_forms(driver)
    taxaudit.fill_taxaudit_forms(driver)
    air.fill_air_forms(driver)
    sft.fill_sft_forms(driver)
    tdspayment.fill_tdspayment_forms(driver)
    tdsreturn.fill_tdsreturn_forms(driver)
    others.fill_others_forms(driver)
    customer.fill_customer_forms(driver)
    purchase.fill_purchase_forms(driver)
    sales.fill_sales_forms(driver)
    income.fill_income_forms(driver)
    expenses.fill_expenses_forms(driver)
    zip_upload.fill_zip_upload_forms(driver)
    ack.fill_ack_forms(driver)
    driver.find_element(By.NAME, "clientview-btn").click()
    time.sleep(2)


    print(f"✅ Completed client {index+1}: {row['client_name']}")
    time.sleep(2)

print("🎉 All clients created and forms filled successfully!")
driver.quit()
