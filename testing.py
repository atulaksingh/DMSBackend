from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeSerice
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import random
from datetime import datetime
import time 

driver = webdriver.Chrome(service=ChromeSerice(ChromeDriverManager().install()))

driver.get("http://localhost:5173/")
time.sleep(1)
driver.find_element(By.CSS_SELECTOR, "a[href='/client'] button").click()

client_name = driver.find_element(By.NAME, "client_name")
client_name.send_keys("Zaco Computers")

dropdown_button = driver.find_element(By.CSS_SELECTOR, "button[name='entity_type']")
dropdown_button.click()
time.sleep(1)  # Allow time for the dropdown options to load

dropdown_options = driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']")

random_option = random.choice(dropdown_options)
print(f"Selected option: {random_option.text}")
random_option.click()

selected_text = dropdown_button.text
print(f"Dropdown now shows: {selected_text}")


# date_input = driver.find_element(By.NAME, "date_of_incorporation")
# # Enter the desired date in the format YYYY-MM-DD
# desired_date = "2025-01-15"  # Example date
# date_input.send_keys(desired_date)
# selected_date = date_input.get_attribute("value")
# print(f"Selected date: {selected_date}")

date_input = driver.find_element(By.NAME, "date_of_incorporation")

# Set the desired date to 24th June 2024
desired_date = "2024-06-24"

# Use JavaScript to set the value directly to the input field
driver.execute_script("arguments[0].value = arguments[1]", date_input, desired_date)

# Verify the selected date
selected_date = date_input.get_attribute("value")
print(f"Selected date: {selected_date}")

contact_name = driver.find_element(By.NAME, "contact_person")
contact_name.send_keys("Atul Singh")

designation = driver.find_element(By.NAME, "designation")
designation.send_keys("CEO")

email = driver.find_element(By.NAME, "email")
email.send_keys("abc@gmail.com")

contact_no_1 = driver.find_element(By.NAME, "contact_no_1")
contact_no_1.send_keys("098765432123")

contact_no_2 = driver.find_element(By.NAME, "contact_no_2")
contact_no_2.send_keys("098765432123")

business_detail = driver.find_element(By.NAME, "business_detail")
business_detail.send_keys("098765432123")

dropdown_button_status = driver.find_element(By.CSS_SELECTOR, "button[name='status']")
dropdown_button_status.click()
time.sleep(1)  # Allow time for the dropdown options to load
dropdown_options = driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']")
random_option = random.choice(dropdown_options)
print(f"Selected option: {random_option.text}")
random_option.click()
selected_text = dropdown_button_status.text
print(f"Dropdown now shows: {selected_text}")

attachment = driver.find_element(By.CSS_SELECTOR, 'label[for="mom-file"]')
attachment.click()

dropdown_button_files = driver.find_element(By.CSS_SELECTOR, "button[name='file_name']")
dropdown_button_files.click()
time.sleep(1)  # Allow time for the dropdown options to load
dropdown_options = driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']")
random_option = random.choice(dropdown_options)
print(f"Selected option: {random_option.text}")
random_option.click()
selected_text = dropdown_button_files.text
print(f"Dropdown now shows: {selected_text}")

login = driver.find_element(By.NAME, "login")
login.send_keys("login")

password = driver.find_element(By.NAME, "password")\
password.send_keys("password")

remark = driver.find_element(By.NAME, "remark")
remark.send_keys("remark")

file_input = driver.find_element(By.NAME, 'file')
file_input.send_keys(r'c:\Users\Abhiraj Das\Downloads\a.txt')
file_input.send_keys(r'c:\Users\Abhiraj Das\Downloads\b.txt')
file_input.send_keys(r'c:\Users\Abhiraj Das\Downloads\c.txt')


upload_button = driver.find_element(By.NAME, "upload")
upload_button.click()

create_button = driver.find_element(By.NAME, "create-btn")
create_button.click()

time.sleep(10000000)
driver.close()
driver.quit()
print("Done")
