import json
import os
import time
import traceback
from datetime import datetime
import logging

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
        extra_data={},
        write_error_webpage=False #TODO: Set this as env var
):
    logging.info(
        f'running monitor image. platform: {platform}, '
        f'local image filepath: {image_filepath},'
        f'and output directory: {output_dir},'
    )
    logging.info(f'extra data: {extra_data}, write_error_webpages: {write_error_webpage}')
    start_time = datetime.now()

    image_filename_base = image_filepath.split("/")[-1].split(".")[0]
    image_filename_base = f'{platform}_{image_filename_base}'

    if platform == 'google':
        monitor_fun = get_google
    elif platform == 'yandex':
        monitor_fun = get_yandex
    else:
        logging.info('platform not recognized!')
        raise NotImplementedError

    try:
        links = monitor_fun(driver, image_filepath)
        logging.info(f'collected {len(links)} links')

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
        logging.info(f'selenium error! ')
        logging.info(str(e))
        logging.info('stack trace:')
        logging.info(traceback.format_exc())

        if write_error_webpage:
            output_filename = os.path.join(output_dir, f'error_{image_filename_base}.html')
            with open(output_filename, "w", encoding='utf-8') as f:
                f.write(driver.page_source)
        else:
            output_filename = 'n.a. (write_error_webpage==False)'
        success = False

    end_time = datetime.now()
    logging.info(f'runtime : {(end_time-start_time).total_seconds()} seconds')

    logging.info(f'result: {"success" if success else "fail"}')
    logging.info(f'local result filename: {output_filename}')
    return success, output_filename


def get_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    logging.info(f'grabbed driver')
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
    logging.info(f'found and clicked reverse image search button')

    # Send the photo file
    photo_upload_selector = "input[type = 'file']"
    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, photo_upload_selector))
    )
    file_input.send_keys(photo_filename)
    logging.info(f'uploaded image')

    # Click on "Find image source" --> Gives exact matches
    exact_matches_selector = 'div[class="ICt2Q"]'
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, exact_matches_selector))
    )
    driver.find_element(By.CSS_SELECTOR, exact_matches_selector).click()
    logging.info(f'found and clicked "find image source" (exact matches) button')

    # Get links
    try:
        link_selector = 'li a'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, link_selector))
        )
        link_elems = driver.find_elements(By.CSS_SELECTOR, link_selector)
        links = [link_elem.get_attribute('href') for link_elem in link_elems]
        logging.info(f'found some exact matches')
    except TimeoutException as e:
        links = []
        logging.info(f'found no exact matches')

    return links


def get_yandex(driver, photo_filename):
    driver.get('https://yandex.com/images/')
    photo_upload_selector = "input[type = 'file']"

    # TODO: Yandex in the cloud fails here
    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, photo_upload_selector))
    )
    file_input.send_keys(photo_filename)
    logging.info(f'uploaded image')

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
    logging.info(f'found exact matches indicator: {"True" if exact_match else "False"}')

    if exact_match:
        link_selector = 'li[class="CbirSites-Item"] div[class="CbirSites-ItemTitle"] a'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, link_selector))
        )
        link_elems = driver.find_elements(By.CSS_SELECTOR, link_selector)
        links = [link_elem.get_attribute('href') for link_elem in link_elems]
        logging.info(f'found links')

    else:
        links = []

    return links


if __name__ == '__main__':
    test_platform = 'google'
    image_filepath = f'{os.getcwd()}/images/public_photo.jpg'
    test_output_dir = f'{os.getcwd()}/tmp'
    driver = get_driver()
    monitor_image(test_platform, image_filepath, test_output_dir, driver)
