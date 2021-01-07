import sys

from selenium import webdriver
import selenium.common.exceptions as Exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import config.epic_config as config


class EpicReservation:

    # TODO Sometimes any page load will give system cannot process your request error.
    #  Need to check for error screen on every action

    def __init__(self, driver=None):
        self._resort = config.resort
        self._year = config.year
        self._month = config.month
        self._day = config.day
        self._email = config.email
        self._password = config.password

        # default to chrome driver but allow firefox
        if driver == "firefox":
            self._driver = webdriver.Firefox(
                executable_path=GeckoDriverManager().install()
            )
        else:
            self._driver = webdriver.Chrome(ChromeDriverManager().install())

        # initialize web driver

        self._driver.get(
            "https://www.epicpass.com/plan-your-trip/lift-access/reservations.aspx"
        )

    def make_reservation(
        self,
    ):
        """ reservation logic """

        self._sign_in()

        reservation_success = False
        while not reservation_success:
            self._load_calendar()
            if self._select_day():
                # day is not disabled
                complete_res = self._complete_reservation()

                reservation_success = complete_res["success"]
                if reservation_success:
                    print(
                        f"\nSUCCESS:Reserved {self._resort} for {self._month}/{self._day}/{self._year} 🥳🎊🎉🎉"
                    )
                    pass
                else:
                    # TODO: Some errors should be fatal i.e. too many
                    #  prior reservations
                    print(
                        f'\nERROR completing reservation:{complete_res["error"]["msg"]}'
                    )
        self._refresh_calendar()
        pass

        input("continue")

    def _sign_in(self):
        # Enter credentials and sign in if form is present
        try:
            if self._driver.find_element_by_id("accountSignIn"):
                # there are multiple login forms, need to make sure selecting correct one
                form_sign_in = self._driver.find_element_by_id(
                    "returningCustomerForm_3"
                )
                input_user = form_sign_in.find_element_by_name("UserName")
                input_password = form_sign_in.find_element_by_name("Password")

                input_user.send_keys(self._email)
                input_password.send_keys(self._password)
                # close dmca notice if present, may block sign in button otherwise
                try:
                    WebDriverWait(self._driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "#onetrust-close-btn-container > button")
                        )
                    ).click()
                except Exceptions.TimeoutException:
                    print("No DMCA notice found")
                WebDriverWait(self._driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//form[@id='returningCustomerForm_3']//button[@class='btn primaryCTA primaryCTA--full accountLogin__cta']",
                        )
                    )
                ).click()

        # NoSuchElementException thrown if sign in form not present
        except Exceptions.NoSuchElementException:
            print("Already logged in!")

    def _load_calendar(self, resort_name=None):
        resort_name = resort_name.title() if resort_name else self._resort.title()
        # Select resort from dropdown
        try:
            resort_selector = WebDriverWait(self._driver, 20).until(
                EC.presence_of_element_located(
                    (By.ID, "PassHolderReservationComponent_Resort_Selection")
                )
            )
            Select(resort_selector).select_by_visible_text(resort_name)
        except Exceptions.NoSuchElementException:
            sys.exit(
                f'\nError finding a resort named "{resort_name}". Check the spelling and try again.'
            )

        # Check availability/load calendar
        self._driver.find_element_by_id("passHolderReservationsSearchButton").click()

    def _refresh_calendar(self):
        # prevent having to reload entire page by checking availability for any other resort and then
        #   checking again for target resort
        temp_resort = self._driver.find_element_by_css_selector(
            "#PassHolderReservationComponent_Resort_Selection > option:nth-child(2)"
        )
        # make sure the intermediary resort is different
        if temp_resort.text.title() == self._resort.title():
            temp_resort = self._driver.find_element_by_css_selector(
                "#PassHolderReservationComponent_Resort_Selectio > option:nth-child(3)"
            )
        self._load_calendar(temp_resort.text)

    def _select_day(self):
        #
        # if day is disabled, then cannot reserve and need to refresh
        return True

    def _complete_reservation(self):
        error_msg = "No reservation for you 😭"
        error_type = "warn"
        return {"success": True, "error": {"type": error_type, "msg": error_msg}}
