from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

def create_driver(initial):
    # Create a Chrome browser controlled by Selenium
    options = Options()

    # Run Chrome without opening a visible browser window
    ## options.add_argument("--headless=new")

    # May help Chrome run on some environments
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Force a desktop-sized viewport
    options.add_argument("--window-size=1600,1200")
    options.add_argument("--force-device-scale-factor=1")

    driver = webdriver.Chrome(options=options)

    # Also set it explicitly after Chrome starts
    driver.set_window_size(1600, 1200)

    driver.get(initial)

    return driver

def get_info(driver):

    # Find the visible introduction for the paragraph to appear
    intro  = WebDriverWait(driver,15).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "section[aria-labelledby='overview'] p"
            )
        )
    )

    # Return the visible text in the section
    return intro.text.strip()

def find_visible_element(driver, selector):
    elements = driver.find_elements(By.CSS_SELECTOR, selector)

    for element in elements:
        if element.is_displayed() and element.is_enabled():
            return element

    return False

def get_next_bird(bird, driver):
    #defining a wait period
    wait = WebDriverWait(driver, 15)

    # Find the search bar or the search button
    search_bar = find_visible_element(driver, "input.Suggest-input")
    if not search_bar:
        search_button = wait.until(
            lambda d: find_visible_element(
                d,
                ".Header-main-search-button"
            )
        )

        search_button.click()

        search_bar = wait.until(
            lambda d: find_visible_element(
                d,
                "input.Suggest-input"
            )
        )

    # saving the current url
    old_url = driver.current_url

    # clearing the search bar, inputting the bird, and pressing the first dropdown
    search_bar.clear()
    search_bar.send_keys(bird)
     # Wait for the autocomplete component to open
    wait.until(
        lambda d: search_bar.get_attribute("aria-expanded") == "true"
    )

    # Select the first autocomplete result
    search_bar.send_keys(Keys.ARROW_DOWN)
    search_bar.send_keys(Keys.RETURN)
    wait.until(EC.url_changes(old_url))

    # get the intro paragraph from the page
    info = get_info(driver)

    return info

def search_for_birds(listOfBirds, initial):

    # creating the driver
    driver = create_driver(initial)


    try:
        # getting all the birds in the bird list
        for bird in listOfBirds:
            print("Searching for", bird)
            info = get_next_bird(bird[0], driver)

            print(f"{bird}:")
            print(info)

    except Exception:

        print("search_for_birds failed:")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        traceback.print_exc()
        # Capture the browser's state for debugging.
        driver.save_screenshot("selenium-error.png")

        with open("page-source.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        raise

        
    finally:
        driver.quit()
