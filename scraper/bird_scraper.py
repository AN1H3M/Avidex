from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

def create_driver():
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

    return driver

def get_info(driver):
    wait = WebDriverWait(driver, 30)

    # Wait until the documnet itself has completely loaded
    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    selectors = [
        "section[aria-labelledby='overview'] p",
        "section[id='overview'] p",
        "[aria-labelledby='overview'] p",
        "section p",
        "main p",
    ]

    def find_visible_text(driver):
        for selector in selectors:
            for element in driver.find_elements(By.CSS_SELECTOR, selector):
                if element.is_displayed():
                    text = element.text.strip()
                    if text:
                        return text
        return False

    try:
        return wait.until(find_visible_text)

    except TimeoutException:
        # Give useful diagnostics instead of only raising an empty timeout.
        print("No visible introduction paragraph found.")
        print("URL:", driver.current_url)
        print("Title:", driver.title)
        print("Body text:", driver.find_element(By.TAG_NAME, "body").text[:2000])

        raise

def find_visible_element(driver, selector):
    elements = driver.find_elements(By.CSS_SELECTOR, selector)

    for element in elements:
        if element.is_displayed() and element.is_enabled():
            return element

    return False

def get_next_bird(bird, driver):
    #defining a wait period
    wait = WebDriverWait(driver, 30)

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

    wait.until(lambda d: d.current_url != old_url)

    # Wait for the new page's main content to appear.
    wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # get the intro paragraph from the page
    info = get_info(driver)

    return info

def search_for_birds(listOfBirds):

    # creating the driver
    driver = create_driver()
    driver.get("https://birdsoftheworld.org/bow/home")

    infolist = []

    try:
        # getting all the birds in the bird list
        count = 0
        for bird in listOfBirds:
            print()
            print("---")
            print()
            print("Searching for", bird)
            info = get_next_bird(bird[0], driver)

            print(count,":",bird)
            print(info)
            count+=1
            infolist.append(info)

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
