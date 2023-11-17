from scraper_util_avliu.util import get_selenium_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = "https://images.google.com"
upload_file = '/Users/avliu/Dropbox (University of Michigan)/projects/monitor_images/test_photo.jpg'

driver = get_selenium_driver()
driver.get(url)

# Get the RIS button
ris_selector = 'svg[class="Gdd5U"]'
cameraicon = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ris_selector))
)
cameraicon.click()

# Send the photo file
photo_upload_selector = "input[type = 'file']"
file_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, photo_upload_selector))
)
file_input.send_keys(upload_file)

# Click on "Find image source" --> Gives exact matches
exact_matches_selector = 'div[class="ICt2Q"]'
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, exact_matches_selector))
)
driver.find_element(By.CSS_SELECTOR, exact_matches_selector).click()

# Get links
link_selector = 'li a'
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, link_selector))
)
link_elems = driver.find_elements(By.CSS_SELECTOR, link_selector)
links = [link_elem.get_attribute('href') for link_elem in link_elems]

print(f'got {len(links)} total links')
print(links)
