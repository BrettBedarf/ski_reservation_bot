import sys

from selenium import webdriver
import selenium.common.exceptions as Exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import config.epic_config as epic_config


def main():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.epicpass.com/plan-your-trip/lift-access/reservations.aspx")

    # TODO Sometimes any page load will give system cannot process your request error. Need to check for error screen on ever action
    # Enter credentials and sign in if form is present
    try:
        if driver.find_element_by_id('accountSignIn'):
            # there are multiple login forms, need to make sure selecting correct one
            form_sign_in = driver.find_element_by_id('returningCustomerForm_3')
            input_user = form_sign_in.find_element_by_name('UserName')
            input_password = form_sign_in.find_element_by_name('Password')

            input_user.send_keys(epic_config.email)
            input_password.send_keys(epic_config.password)

            # driver.find_element_by_css_selector('#onetrust-close-btn-container > button').click()
            # close dmca notice
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#onetrust-close-btn-container > button'))).click()
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//form[@id='returningCustomerForm_3']//button[@class='btn primaryCTA primaryCTA--full accountLogin__cta']"))).click()

    # NoSuchElementException thrown if sign in form not present
    except Exceptions.NoSuchElementException:
        print('Already logged in!')

    # Select resort from dropdown
    try:
        resort_selector = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.ID,
                 'PassHolderReservationComponent_Resort_Selection')))
        Select(resort_selector).select_by_visible_text(
            epic_config.resort)
    except Exceptions.NoSuchElementException:
        sys.exit(f'\nError finding a resort named "{epic_config.resort}". Check the spelling and try again.')

    # Check availability/load calendar
    driver.find_element_by_id('passHolderReservationsSearchButton').click()

    input('Any key to exit...')


if __name__ == '__main__':
    main()
