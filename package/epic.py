import sys

from selenium import webdriver
import selenium.common.exceptions as Exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import config.epic_config as config


class EpicReservation:
    """Contains logic for reserving at an epic pass resort"""

    # TODO Sometimes any page load will give system cannot process your request error.
    #  Need to check for error screen on every action

    def __init__(self, ):
        self._resort = config.resort
        self._year = config.year
        self._month = config.month
        self._day = config.day
        self._email = config.email
        self._password = config.password

        # initialize web driver
        self._driver = webdriver.Chrome(ChromeDriverManager().install())
        self._driver.get("https://www.epicpass.com/plan-your-trip/lift-access/reservations.aspx")

        # reservation logic
        self._sign_in()
        self._load_calendar()

    def _sign_in(self):
        # Enter credentials and sign in if form is present
        try:
            if self._driver.find_element_by_id('accountSignIn'):
                # there are multiple login forms, need to make sure selecting correct one
                form_sign_in = self._driver.find_element_by_id('returningCustomerForm_3')
                input_user = form_sign_in.find_element_by_name('UserName')
                input_password = form_sign_in.find_element_by_name('Password')

                input_user.send_keys(self._email)
                input_password.send_keys(self._password)
                # close dmca notice if present, may block sign in button otherwise
                try:
                    WebDriverWait(self._driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, '#onetrust-close-btn-container > button'))).click()
                except Exceptions.TimeoutException:
                    print('No DMCA notice found')
                WebDriverWait(self._driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "//form[@id='returningCustomerForm_3']//button[@class='btn primaryCTA primaryCTA--full accountLogin__cta']"))).click()

        # NoSuchElementException thrown if sign in form not present
        except Exceptions.NoSuchElementException:
            print('Already logged in!')

    def _load_calendar(self):
        # Select resort from dropdown
        try:
            resort_selector = WebDriverWait(self._driver, 20).until(
                EC.presence_of_element_located(
                    (By.ID,
                     'PassHolderReservationComponent_Resort_Selection')))
            Select(resort_selector).select_by_visible_text(
                self._resort)
        except Exceptions.NoSuchElementException:
            sys.exit(f'\nError finding a resort named "{self._resort}". Check the spelling and try again.')

        # Check availability/load calendar
        self._driver.find_element_by_id('passHolderReservationsSearchButton').click()
