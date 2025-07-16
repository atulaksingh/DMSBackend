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
import owner
import bank
import branch
import branchdoc
import companydoc
import customer
import purchase
import sales
import income
import expenses
import zip_upload

# Setup the WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("http://localhost:5173/")
time.sleep(2)

# Read data from Excel file
df = pd.read_excel(r"client.xlsx")  # Modify path as needed

# Convert date_of_incorporation to MM-DD-YYYY format
df["date_of_incorporation"] = pd.to_datetime(df["date_of_incorporation"]).dt.strftime("%m-%d-%Y")

# Loop through each row in the Excel file and fill the form dynamically
for index, row in df.iterrows():
    driver.find_element(By.CSS_SELECTOR, "a[href='/client'] button").click()  
    
    # Fill client name
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

    # Select date of incorporation (Handling MM-DD-YYYY format)
    date_input = driver.find_element(By.NAME, "date_of_incorporation")
    date_input.click()
    time.sleep(1)  # Allow calendar to open
    date_input.send_keys(Keys.CONTROL + "a")  # Select existing date (if any)
    date_input.send_keys(Keys.BACKSPACE)  # Clear existing date
    date_input.send_keys(row["date_of_incorporation"])  # Enter date in MM-DD-YYYY format
    date_input.send_keys(Keys.ENTER)  # Confirm selection

    # Fill other form fields
    driver.find_element(By.NAME, "contact_person").send_keys(row["contact_person"])
    driver.find_element(By.NAME, "designation").send_keys(row["designation"])
    driver.find_element(By.NAME, "email").send_keys(row["email"])
    driver.find_element(By.NAME, "contact_no_1").send_keys(row["contact_no_1"]) 
    driver.find_element(By.NAME, "contact_no_2").send_keys(row["contact_no_2"])
    driver.find_element(By.NAME, "business_detail").send_keys(row["business_detail"])

    # Select status
    dropdown_button_status = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='status']"))
    )
    dropdown_button_status.click()

    dropdown_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']"))
    )
    if dropdown_options:
        random.choice(dropdown_options).click()

    # Handle attachment section
    driver.find_element(By.CSS_SELECTOR, 'label[for="mom-file"]').click()
    dropdown_button_files = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='file_name']"))
    )
    dropdown_button_files.click()

    dropdown_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']"))
    )
    if dropdown_options:
        random.choice(dropdown_options).click()

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
    driver.find_element(By.NAME, "create-btn").click()

    time.sleep(2)

driver.find_element(By.ID, "long-button").click()

client


# view_button = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root")
view_button = driver.find_element(By.NAME, "clientview-btn")
view_button.click()
time.sleep(5)
if not view_button:
    print("view_buton not found")

# owner.fill_owner_forms(driver)
# bank.fill_bank_forms(driver) 
# owner.fill_owner_forms(driver)
bank.fill_bank_forms(driver)

                                 

# Wait before closing
time.sleep(10)
driver.quit()
print("form submitted successfully")
