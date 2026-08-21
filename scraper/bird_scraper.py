from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
)
import csv
from pathlib import Path
import requests
import traceback

WAIT_SECONDS = 1





def send_discord_message(message, username = "Bird Scraper"):
    webhook = os.getenv("DISCORD_WEBHOOK")

    if not webhook:
        raise ValueError(
            "DISCORD_WEBHOOK_URL is missing from the .env file"
        )

    # Discord messages have a 2000 character content limit
    message = message[:2000]

    response = requests.post(
        webhook,
        json = {
            "username": username,
            "content": message,
        },
        timeout = 10,
    )

    response.raise_for_status()




def create_driver():
    # Create a Chrome browser controlled by Selenium
    options = Options()

    # Run Chrome without opening a visible browser window
    options.add_argument("--headless=new")

    # May help Chrome run on some environments
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

     # Do not wait for every image, stylesheet, and subresource.
    options.page_load_strategy = "eager"

    # Images are not needed for scraping text.
    options.add_argument("--blink-settings=imagesEnabled=false")

    # Removes images
    options.add_experimental_option(
        "prefs",
        {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
        },
    )

    # Force a desktop-sized viewport
    options.add_argument("--window-size=1600,1200")
    options.add_argument("--force-device-scale-factor=1")

    driver = webdriver.Chrome(options=options)

    # Removes images
    driver.execute_cdp_cmd(
        "Network.setBlockedURLs",
        {
            "urls": [
                "*.png",
                "*.jpg",
                "*.jpeg",
                "*.gif",
                "*.webp",
                "*.svg",
                "*.woff",
                "*.woff2",
                "*google-analytics.com*",
                "*googletagmanager.com*",
            ]
        },
    )

    # Also set it explicitly after Chrome starts
    driver.set_window_size(1600, 1200)

    driver.set_page_load_timeout(20)
    driver.set_script_timeout(10)

    return driver






def find_visible_element(driver, selector):
    elements = driver.find_elements(By.CSS_SELECTOR, selector)

    for element in elements:
        try:
            if element.is_displayed() and element.is_enabled():
                return element
        except StaleElementReferenceException:
            # The page may have re-rendered the element.
            continue

    return False






def get_info(driver):
    wait = WebDriverWait(driver, WAIT_SECONDS)

    # Wait until the documnet itself has completely loaded
    #wait.until(
    #    lambda d: d.execute_script("return document.readyState") == "complete"
    #)

    selectors = [
        "section[aria-labelledby='overview'] p",
        "section[id='overview'] p",
        "[aria-labelledby='overview'] p",
        "section p",
        "main p",
    ]

    #  Return all visible paragraphs in the overview section. Selenium's element.text excludes hidden reference-panel text.
    def get_overview_text(driver):
        sections = driver.find_elements(
            By.CSS_SELECTOR,
            "section[aria-labelledby='overview']"
        )
        for section in sections:
            if not section.is_displayed():
                continue

            paragraphs = section.find_elements(By.CSS_SELECTOR,"p")

            text_parts = []

            for paragraph in paragraphs:
                if paragraph.is_displayed():
                    text = paragraph.text.strip()

                    if text:
                        text_parts.append(text)

            if text_parts:
                # Separate paragraphs with bank lines
                return "\n\n".join(text_parts)
            
        return False

    try:
        return wait.until(get_overview_text)

    except TimeoutException:
        # Give useful diagnostics instead of only raising an empty timeout.
        print("No overview text found.")
        print("URL:", driver.current_url)
        print("Title:", driver.title)
        print("Body text:", driver.find_element(By.TAG_NAME, "body").text[:2000])

        raise






def select_search_result(driver, bird_name, wait):
    """
    Select the autocomplete result whose visible text exactly matches
    the requested common name.

    This is safer than blindly pressing ARROW_DOWN because the first
    autocomplete result may not be the requested bird.
    """
    target = " ".join(bird_name.lower().split())

    # These selectors cover common autocomplete implementations.
    option_selectors = [
        "[role='option']",
        ".Suggest-item",
        ".Suggest-list li",
        ".Suggest-results li",
        ".Suggest-suggestion div",
        ".Suggest-cursor div",
        ".Suggestion-text span"
    ]

    def find_matching_option(driver):
        for selector in option_selectors:
            options = driver.find_elements(By.CSS_SELECTOR, selector)

            for option in options:
                try:
                    if not option.is_displayed():
                        continue

                    option_text = " ".join(option.text.lower().split())

                    # Match the common name exactly. This prevents
                    # selecting a similarly named bird.
                    if option_text == target:
                        return option

                except StaleElementReferenceException:
                    continue

        return False

    try:
        matching_option = wait.until(find_matching_option)
        driver.execute_script(
            "arguments[0].click();",
            matching_option
        )

    except TimeoutException:
        # If the site's autocomplete markup does not expose selectable
        # options with the selectors above, use keyboard navigation as
        # a fallback.
        search_bar = wait.until(
            lambda d: find_visible_element(
                d,
                "input.Suggest-input"
            )
        )

        search_bar.send_keys(Keys.ARROW_DOWN)
        search_bar.send_keys(Keys.RETURN)






def get_next_bird(bird, driver):
    #defining a wait period
    wait = WebDriverWait(driver, WAIT_SECONDS)

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
    old_title = driver.title

    # clearing the search bar, inputting the bird, and pressing the first dropdown
    search_bar.clear()
    search_bar.send_keys(Keys.COMMAND, "a")
    search_bar.send_keys(Keys.BACKSPACE)
    search_bar.send_keys(bird)

     # Wait for the autocomplete component to open
    wait.until(
        lambda d: search_bar.get_attribute("aria-expanded") == "true"
    )

    # Select the exact matching autocomplete result.
    select_search_result(driver, bird, wait)

    # Do not rely only on URL changes. The site may reuse a URL or
    # update the title/content before the URL changes.
    wait.until(
        lambda d: (
            d.current_url != old_url
            or d.title != old_title
        )
    )

    # Extract the complete Introduction section.
    return get_info(driver)






# Meant to save failed birds to a csv with it's name, species, and traceback and page html
def save_failed_birds_in_csv(failed_birds, output_path = "data/failed_birds.csv"):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        encoding = "utf-8",
        newline=""
    ) as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow([
            "common_name",
            "species",
        ])

        writer.writerows(failed_birds)

    print(f"Saved {len(failed_birds)} failed birds to {output_path}")
    






def search_for_birds(list_of_birds, failed_csv_path = "data/failed_birds.csv"):

    # creating the driver
    driver = create_driver()

    failed_csv_path = Path(failed_csv_path)
    failed_csv_path.parent.mkdir(parents=True, exist_ok=True)

    scraped_birds = []
    failed_birds = []

    try:

        driver.get("https://birdsoftheworld.org/bow/home")

        # Open the CSV once and keep it open during the scrape.
        with failed_csv_path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as failed_file:

            writer = csv.writer(failed_file)

            writer.writerow([
                "common_name",
                "species",
                "page_url",
                "traceback",
                "html",
            ])


            # getting all the birds in the bird list
            for count, bird in enumerate(list_of_birds):
                common_name, species = bird

                print()
                print("---")
                print()
                print("Searching for:", common_name)

                try:
                    info = get_next_bird(common_name, driver)

                    scraped_birds.append(
                        (
                            common_name,
                            species,
                            info,
                        )
                    )

                    print(f"{count + 1}: Successfully scraped {common_name}")

                except Exception:
                    # save the failed page, record the bird, and continue with the next row instead of aborting the whole scraper
                    print(
                        f"Failed to scrape: "
                        f"{common_name} ({species})"
                    )

                    # capture the page_url
                    page_url = driver.current_url

                    # capture the traceback in a string
                    error_traceback = traceback.format_exc()

                    # capture the html from the page
                    try: 
                        page_html = driver.page_source
                    except Exception:
                        page_html = ""

                    print(
                        f"{count + 1}: Failed to scrape:"
                        f"{common_name} ({species})"
                    )
                    

                    failed_birds.append(
                        (
                            common_name,
                            species,
                        )
                    )

                    # Write the failed bird and diagnostics to the CSV.
                    writer.writerow([
                        common_name,
                        species,
                        page_url,
                        error_traceback,
                        page_html,
                    ])

                    # Make sure the row is physically written immediately.
                    failed_file.flush()

                    # continuing to the next bird
                    continue

                if count+1 % 100 == 0:

                    check_in_message = (
                        f"Bird scraper at: {count+1}\n"
                        f"Error: {type(error).__name__}: {error}\n"
                        f"Successful so far: {len(scraped_birds)} birds.\n"
                        f"Failed so far: {len(failed_birds)} birds."
                    )
                    
                    try:
                        send_discord_message(
                            check_in_message,
                            username="Bird Scraper",
                        )
                    except Exception as notification_error:
                        print(
                            "Could not send failure Discord message:",
                            notification_error,
                        )

        
    finally:
        driver.quit()

    # Save the CSV after the scraping loop finishes.
    save_failed_birds_in_csv(
        failed_birds,
        failed_csv_path
    )


    print()
    print("---")
    print("---")
    print("---")
    print("Scraping complete.")
    print("Successful birds:", len(scraped_birds))
    print("Failed birds:", len(failed_birds))

    if failed_birds:
        print("Failed bird list:")
        for bird in failed_birds:
            print(" -", bird)

    return scraped_birds, failed_birds
