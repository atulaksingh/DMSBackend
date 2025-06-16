import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import officelocation

def fill_branchdoc_forms(driver):
    # Load the Excel data
    df = pd.read_excel(r"updateclient.xlsx")

    # Wait for branch table to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )

    # Get all branch rows
    client_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'MuiTableRow-root MuiTableRow-hover')]")

    print(f"Total Client Found: {len(client_rows)}")

    for i in range(len(client_rows)):
        # Re-fetch the list of branches to avoid stale elements
        client_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'MuiTableRow-root MuiTableRow-hover')]")

        if i >= len(client_rows):
            print(f"Client index {i} out of range, stopping loop.")
            break

        try:
            view_button = client_rows[i].find_element(By.XPATH, ".//button[@id='long-button']")
            driver.execute_script("arguments[0].scrollIntoView();", view_button)  # Scroll if not visible
            time.sleep(1)
            view_button.click()
            time.sleep(2)

            # button = driver.find_element(By.XPATH, "//button[contains(text(), 'Branch Details')]")

            # Click the dropdown option (assuming it's the first option)
            dropdown_option = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'Update')]")
            ))
            dropdown_option.click()
            time.sleep(3)

            print(f"Opened Client {i + 1}")

        except Exception as e:
            print(f"Error clicking View button for Client {i + 1}: {e}")
            continue

        # Add 10 branch document records for this branch
        for index, row in df.iterrows():
            # try:
            #     button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
            #     button.click()
            # except Exception as e:
            #     print(f"Error clicking Create button: {e}")
            #     continue
            # time.sleep(5)

            try:



                # Fill other form fields
                contact = driver.find_element(By.NAME, "contact_person")
                contact.clear()
                contact.send_keys(row["contact_person"])

                designation = driver.find_element(By.NAME, "designation")
                designation.clear()
                designation.send_keys(row["designation"])
                time.sleep(1)

                email = driver.find_element(By.NAME, "email")
                email.clear()
                email.send_keys(row["email"])
                time.sleep(1)


                contact1 = driver.find_element(By.NAME, "contact_no_1")
                contact1.clear()
                contact1.send_keys(row["contact_no_1"])
                time.sleep(1)


                contact2 = driver.find_element(By.NAME, "contact_no_2")
                contact2.clear()
                contact2.send_keys(row["contact_no_2"])
                time.sleep(1)

                delete_icon = driver.find_element(By.XPATH, "//svg[@data-testid='ControlPointIcon']")

                # Click the delete icon
                delete_icon.click()


                # driver.find_element(By.CSS_SELECTOR, 'label[for="mom-file"]').click()
                # dropdown_button_files = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='file_name']"))
                # )
                # dropdown_button_files.click()

                # Locate the <span> inside <li> without specifying text
                span_element = driver.find_element(By.XPATH, "//li[contains(@class, 'flex')]//span")

                # Click the found <span>
                span_element.click()

                remark = driver.find_element(By.NAME, "remark")
                remark.clear()
                remark.send_keys(row["remark"])
                time.sleep(1)



                driver.find_element(By.XPATH, "//button[contains(text(), 'Upload')]").click()

                # delete_icon = driver.find_element(By.XPATH, "//svg[@data-testid='DeleteIcon']")

                # # Click the delete icon
                # delete_icon.click()
                # driver.find_element(By.XPATH, "//button[contains(text(), 'Update')]").click()
                # update_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Update')]")
                # update_button.click()
                # Locate the button using XPath
                update_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Update')]")

                # Scroll to the button
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", update_button)

                # Wait for scrolling effect
                time.sleep(1)

                # Click the button
                update_button.click()



            except Exception as e:
                print(f"Error filling form for row {index}: {e}")
                continue

            time.sleep(5)

        # Navigate back to the branch list before going to the next branch
        print(f"Exiting Branch {i + 1}...")

        # 
        




if __name__ == "__main__":

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get("http://localhost:5173/")
    time.sleep(2)

    fill_branchdoc_forms(driver)
    time.sleep(15)
    driver.quit()
    print("Client form Updation done.")

    

