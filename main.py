from selenium import webdriver
import selenium.common.exceptions as Exceptions
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import config.epic_config as epic_config


def main():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.epicpass.com/plan-your-trip/lift-access/reservations.aspx")

    # Enter credentials and sign in if form is present
    try:
        if driver.find_element_by_id('accountSignIn'):
            # there are multiple login forms, need to make sure selecting correct one
            form_sign_in = driver.find_element_by_id('returningCustomerForm_3')
            input_user = form_sign_in.find_element_by_name('UserName')
            input_password = form_sign_in.find_element_by_name('Password')
            button_sign_in = form_sign_in.find_element_by_css_selector('.btn.accountLogin__cta')

            input_user.send_keys(epic_config.email)
            input_password.send_keys(epic_config.password)
            button_sign_in.click()

    # NoSuchElementException thrown if sign in form not present
    except Exceptions.NoSuchElementException:
        print('Already logged in!')

    input('Any key to exit...')


if __name__ == '__main__':
    main()
