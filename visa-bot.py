from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


TIMEOUT = 20

# how many available slots do I want
NUM_SLOT = 50

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

WebDriverWait(browser, timeout=TIMEOUT).until(
    EC.visibility_of_element_located((By.ID, "consulate-appointment-fields"))
)

# choose location

Select(
    browser.find_element(By.ID, "appointments_consulate_appointment_facility_id")
).select_by_visible_text("Toronto")

# wait until the page is updated

WebDriverWait(browser, TIMEOUT).until(
    EC.none_of(
        EC.text_to_be_present_in_element_attribute(
            (By.ID, "appointments_consulate_address"), "style", "opacity"
        )
    )
)

# abort on error

if "display: block;" in browser.find_element(
    By.ID, "consulate_date_time_not_available"
).get_attribute("style"):
    raise Exception("There are no available appointments at the selected location.")

# open calendar

WebDriverWait(browser, timeout=TIMEOUT).until(
    EC.element_to_be_clickable((By.ID, "appointments_consulate_appointment_date"))
).click()

# go through calendar

slots = list()
year = None
month = None

while len(slots) < NUM_SLOT:
    # make sure the calendar is updated after clicking next
    while True:
        first = browser.find_element(
            By.XPATH,
            '//*[contains(@class ,"ui-datepicker-group")][contains(@class ,"ui-datepicker-group-first")]',
        )

        year_new = first.find_element(By.CLASS_NAME, "ui-datepicker-year").text
        month_new = first.find_element(By.CLASS_NAME, "ui-datepicker-month").text

        if (year is None and month is None) or year_new != year or month_new != month:
            year = year_new
            month = month_new
            break

        browser.implicitly_wait(1)

    for item in (
        first.find_element(By.CLASS_NAME, "ui-datepicker-calendar")
        .find_element(By.TAG_NAME, "tbody")
        .find_elements(By.TAG_NAME, "td")
    ):
        if "ui-datepicker-unselectable" in item.get_attribute("class"):
            continue

        day = item.find_element(By.CLASS_NAME, "ui-state-default").text

        slots.append(f"{month}-{day}-{year}")

    browser.find_element(
        By.XPATH,
        '//*[contains(text(), "Next")][contains(@class ,"ui-icon")][contains(@class ,"ui-icon-circle-triangle-e")]',
    ).click()

print(f"The earliest {NUM_SLOT} available slots are:")
print("\n".join(slots))

browser.quit()
