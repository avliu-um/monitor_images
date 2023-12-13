import os
import time
import traceback

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def monitor_images(platform, local_image_filename, driver):
    if platform == 'google':
        links = get_google(driver, local_image_filename)
    elif platform == 'yandex':
        links = get_yandex(driver, local_image_filename)
    else:
        print('crying')
        raise NotImplementedError

    print(f'links: {links}')

    return links

def get_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    print(f'grabbed driver')
    return driver

def get_google(driver, photo_filename):
    url = "https://images.google.com"
    driver.get(url)

    # Get the RIS button
    ris_selector = 'svg[class="Gdd5U"]'
    cameraicon = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ris_selector))
    )
    cameraicon.click()
    print(f'found and clicked reverse image search button')

    # Send the photo file
    photo_upload_selector = "input[type = 'file']"
    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, photo_upload_selector))
    )
    file_input.send_keys(photo_filename)
    print(f'uploaded image')

    # Click on "Find image source" --> Gives exact matches
    exact_matches_selector = 'div[class="ICt2Q"]'
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, exact_matches_selector))
    )
    driver.find_element(By.CSS_SELECTOR, exact_matches_selector).click()
    print(f'found and clicked "find image source" (exact matches) button')

    # Get links
    link_selector = 'li a'
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, link_selector))
    )
    link_elems = driver.find_elements(By.CSS_SELECTOR, link_selector)
    links = [link_elem.get_attribute('href') for link_elem in link_elems]
    print(f'found links')

    return links


def get_yandex(driver, photo_filename):
    driver.get('https://yandex.com/images/')
    photo_upload_selector = "input[type = 'file']"
    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, photo_upload_selector))
    )
    file_input.send_keys(photo_filename)
    print(f'uploaded image')

    time.sleep(30)

    # Answers the Q: Are the links we grab below exact matches or no?
    exact_match = True
    try:
        exact_matches_empty_selector = 'div[class="CbirOtherSizes-EmptyMessage"]'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, exact_matches_empty_selector))
        )
        exact_match = False
    except TimeoutException as e:
        pass
    print(f'found exact matches indicator: {"True" if exact_match else "False"}')

    if exact_match:
        link_selector = 'li[class="CbirSites-Item"] div[class="CbirSites-ItemTitle"] a'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, link_selector))
        )
        link_elems = driver.find_elements(By.CSS_SELECTOR, link_selector)
        links = [link_elem.get_attribute('href') for link_elem in link_elems]
        print(f'found links')

    else:
        links = []

    return links


def main():
    image_path = os.environ.get('image_path')
    print(f'image path: {image_path}')

    platform = os.environ.get('platform')
    print(f'platform: {platform}')

    driver = get_driver()
    try:
        links = monitor_images(platform, image_path, driver)

        print(f'got {len(links)} total links: ')
        print(links)

    except Exception as e:
        print(f'Exception: {e}')
        traceback.print_exc()
        with open("exception_webpage.html", "w", encoding='utf-8') as f:
            f.write(driver.page_source)


if __name__ == '__main__':
    main()
