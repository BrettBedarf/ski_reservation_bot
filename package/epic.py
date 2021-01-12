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
from package.date_util import month_names


class EpicReservation:

    # TODO Sometimes any page load will give system cannot process your request error.
    #  Need to check for error screen on every action

    def __init__(self, driver=None):
        self._resort = config.resort
        self._year = config.year
        self._month = config.month
        self._month_name = month_names[config.month - 1]
        self._day = config.day
        self._email = config.email
        self._password = config.password
        self._phone = config.phone

        # initialize web driver

        # default to chrome driver but allow firefox
        if driver == "firefox":
            self._driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        else:
            self._driver = webdriver.Chrome(ChromeDriverManager().install())

        # initialize web driver

        self._driver.get("https://www.epicpass.com/plan-your-trip/lift-access/reservations.aspx")

    def make_reservation(
        self,
    ):
        """ Epic reservation logic """

        self._driver.get("https://www.epicpass.com/plan-your-trip/lift-access/reservations.aspx")

        self._sign_in()
        self._load_calendar()

        reservation_success = False
        while not reservation_success:
            if self._select_day():
                # day is not disabled
                submit_response = self._submit_reservation()

                reservation_success = submit_response["success"]
                if reservation_success:
                    print(
                        f"\nSUCCESS:Reserved {self._resort} for {self._month}/{self._day}/{self._year} 🥳🎊🎉🎉"
                    )
                    break
                else:
                    # TODO: Some errors should be fatal i.e. too many
                    #  prior reservations
                    print(f'\nERROR completing reservation:{submit_response["error"]["msg"]}')
            # refresh page if either day is unavailable or non-fatal error completing form
            self._refresh_calendar()

        input("continue")

    def _sign_in(self):
        # Enter credentials and sign in if form is present
        try:
            if self._driver.find_element_by_id("accountSignIn"):
                # there are multiple login forms, need to make sure selecting correct one
                form_sign_in = self._driver.find_element_by_id("returningCustomerForm_3")
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
        self._load_calendar()

    def _select_day(self):
        calendar = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "passholder_reservations__calendar"))
        )

        # select month
        while (
            calendar.find_element_by_xpath(
                '//*[@class="passholder_reservations__calendar_name c111__datettitle--v1"]'
            ).text.lower()
            != self._month_name.lower()
        ):
            # wrong month, click right arrow
            next_month_btn = calendar.find_element_by_class_name(
                "passholder_reservations__calendar__arrow--right"
            )
            # check and throw exception if month is not available
            if next_month_btn.is_enabled():
                next_month_btn.click()
            else:
                raise Exception(f"{self._month_name} is not available at {self._resort}!")

            # wait for loading spinner to be visible and again for it to dissapear
            try:
                calendar_wait = WebDriverWait(calendar, 10)
                spinner = calendar_wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@class="inline_loading_spinner"]')
                    )
                )
                calendar_wait.until(EC.staleness_of(spinner))
            except:
                # assume we didn't catch the spinner loading because data loaded
                # too quickly
                print(
                    "Didn't see the spinner loading and unloading. Continuing execution anyways.."
                )
                pass
            print("pause")

        # get day element
        cal_days = calendar.find_elements_by_class_name("passholder_reservations__calendar__day")

        try:
            day = next(
                (day for day in cal_days if int(day.text) == self._day)
            )  # using list comprehension to filter
        except StopIteration:
            raise Exception(
                "Selected day not found in calendar!"
            )  # day existing should have been validated beforehand

        # if day is disabled, then cannot reserve and need to refresh
        if day.is_enabled():
            day.click()
            return True
        else:
            return False

        # TODO handle not yet available days

    def _submit_reservation(self):
        """ Logic to fill and submit reservation form. Returns success or error message. """

        wait = WebDriverWait(self._driver, 5)

        assign_passholders_modal = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".passholder_reservations__assign_passholder_modal")
            )
        )
        assign_passholders_button = assign_passholders_modal.find_element_by_css_selector(
            ".primaryCTA"
        )
        # Some accounts may have multiple pass holders. Check all by default for now.
        # Account owners can manually remove any passholders they don't want included.
        checkboxes = assign_passholders_modal.find_elements_by_css_selector(
            'input[type="checkbox"]'
        )
        for checkbox in checkboxes:
            # Actual checkbox is hidden in browser and will not display as checked.
            # Passholders are still selected correctly even if visual box is not checked.
            checkbox.click()
        assign_passholders_button.click()
        # TODO check for already reserved that day error happens in the modal

        # fill form
        form = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "passholder_reservations__completion"))
        )
        phone_field = form.find_element_by_id("reservations-phone")
        email_field = form.find_element_by_id("reservations-email")
        txt_opt_in_box = form.find_element_by_id("contact-opt-in")
        tos_box = form.find_element_by_id("terms-accepted")
        complete_res_btn = form.find_element_by_class_name("primaryCTA")

        phone_field.send_keys(self._phone)
        # Email should already be pre-filled with account holder's.
        # Double check to be sure and replace if necessary
        if email_field.get_attribute("value") != self._email:
            email_field.clear()
            email_field.send_keys(self._email)
        # input box checks will probably not visibly show in browser but input will count
        txt_opt_in_box.click()
        tos_box.click()
        complete_res_btn.click()

        success = False
        error_msg = ''
        error_type = None

        # check for success
        try:
            # TODO not sure if this will still display on failure or not
            wait.until(EC.presence_of_element_located((By.CLASS_NAME,"reservation_confirmation")))
            success = True
            
        except:
            # TODO if no confirmation, get error message
            error_msg = "error confirming"
            # fatal error type would be something that retrying cannot fix
            # i.e bad phone number 
            error_type = "warn"

        return {"success": success, "error": {"type": error_type, "msg": error_msg}}
