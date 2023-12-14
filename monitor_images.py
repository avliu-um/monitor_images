import json
import os
import time
import traceback

from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def monitor_image(
        platform,
        image_filepath,
        output_dir,
        driver,
        extra_data={}
):
    print(
        f'Running monitor image for platform {platform}, '
        f'local image filepath {image_filepath},'
        f'and output directory {output_dir},'
    )

    image_filename_base = image_filepath.split("/")[-1].split(".")[0]
    image_filename_base = f'{platform}_{image_filename_base}'

    if platform == 'google':
        monitor_fun = get_google
    elif platform == 'yandex':
        monitor_fun = get_yandex
    else:
        print('platform not recognized!')
        raise NotImplementedError

    try:
        links = monitor_fun(driver, image_filepath)
        print(f'links: {links}')

        data = []
        for link in links:
            data.append(
                {
                    'link': link,
                    'platform': platform
                }
                | extra_data
            )

        output_filename = os.path.join(output_dir, f'links_{image_filename_base}.json')
        with open(output_filename, 'w') as fp:
            json.dump(data, fp, indent=4, separators=(',', ': '))

        success = True

    except WebDriverException as e:
        print(f'selenium error! ')
        print(str(e))
        print('stack trace:')
        traceback.print_exc()

        output_filename = os.path.join(output_dir, f'error_{image_filename_base}.html')
        with open(output_filename, "w", encoding='utf-8') as f:
            f.write(driver.page_source)

        success = False

    print(f'Result: {"success" if success else "fail"}')
    print(f'Local result filename: {output_filename}')
    return success, output_filename


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

    # TODO: Yandex in the cloud fails here
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


if __name__ == '__main__':
    test_platform = 'google'
    image_filepath = f'{os.getcwd()}/images/public_photo.jpg'
    test_output_dir = f'{os.getcwd()}/tmp'
    driver = get_driver()
    monitor_image(test_platform, image_filepath, test_output_dir, driver)
