from datetime import date

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from package.date_util import month_names


class Reservation:
    def __init__(self, input_data, driver=None):
        self._resort = input_data["resort"]
        self._date = input_data["date"]
        self._year = self._date.year
        self._month = self._date.month
        self._month_name = month_names[self._month - 1]
        self._day = self._date.day
        self._email = input_data["email"]
        self._password = input_data["password"]
        self._phone = input_data["phone"] or "9999999999"

        # initialize web driver
        #   default to chrome driver but allow firefox
        if driver == "firefox":
            self._driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        else:
            self._driver = webdriver.Chrome(ChromeDriverManager().install())

    def process(
        self,
    ):
        """ Base algorithm which uses child class methods to implement"""

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

    # Methods will be overwritten by child classes
    def _sign_in():
        None

    def _load_calendar():
        None

    def _refresh_calendar():
        None

    def _select_day():
        None

    def _submit_reservation():
        None
