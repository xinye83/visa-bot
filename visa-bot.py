from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sys
from pathlib import Path

TIMEOUT = 20

USERNAME, PASSWORD = Path("SECRETS").read_text().strip("\n").split("\n")

browser = webdriver.Chrome()
browser.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_in")

# logging in

WebDriverWait(browser, timeout=TIMEOUT).until(
    EC.visibility_of_element_located((By.ID, "sign_in_form"))
)

browser.find_element(By.ID, "user_email").send_keys(USERNAME)
browser.find_element(By.ID, "user_password").send_keys(PASSWORD)
browser.find_element(By.CLASS_NAME, "icheckbox").click()
browser.find_element(By.NAME, "commit").click()

# continue

WebDriverWait(browser, timeout=TIMEOUT).until(
    EC.visibility_of_element_located((By.LINK_TEXT, "Continue"))
).click()

# unfold reschedule appointment

WebDriverWait(browser, timeout=TIMEOUT).until(
    EC.visibility_of_element_located((By.LINK_TEXT, "Reschedule Appointment"))
).click()

# click reschedule appointment

WebDriverWait(browser, timeout=TIMEOUT).until(
    EC.visibility_of_element_located(
        (
            By.XPATH,
            '//*[contains(text(), "Reschedule Appointment")][contains(@class ,"button")][contains(@class ,"small-only-expanded")]',
        )
    )
).click()

# abort on error

WebDriverWait(browser, timeout=TIMEOUT).until(
    EC.visibility_of_element_located((By.ID, "consulate-appointment-fields"))
)

try:
    browser.find_element(By.ID, "consulate_date_time_not_available")
    print(
        "There are no available appointments at the selected location. Please try again later."
    )
    sys.exit(1)
except NoSuchElementException:
    pass

browser.quit()
