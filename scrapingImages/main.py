from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
import os
import requests
import time
import re
import mimetypes

def get_unique_filename(directory, base_filename):
    filename, extension = os.path.splitext(base_filename)
    index = 1
    while os.path.exists(os.path.join(directory, base_filename)):
        base_filename = f"{filename}_{index}{extension}"
        index += 1
    return base_filename

def sanitize_filename(title):
    sanitized_title = re.sub(r'[\\/*?:"<>|]', '_', title)
    sanitized_title = sanitized_title.replace("/", "-")
    return sanitized_title

url = ""
dir_title = "images"

images_to_scrape = 318

os.makedirs(dir_title, exist_ok=True)

driver = webdriver.Chrome()
driver.get(url)

images_processed = 26

# img_element = driver.find_element("xpath", "//*[@id='photoFrame155801868']/div/a")
# img_element.click()
# time.sleep(1)

while images_processed < images_to_scrape:
    try:
        try:
            img_title = driver.find_element("xpath", "//*[@id='webs-bin-null']/div/div/div/h2").text
        except:
            img_title = "original"

        # Sanitize the title for use in filenames
        sanitized_img_title = sanitize_filename(img_title)

        img_extension = ".jpg"
        img_name = f"{sanitized_img_title}{img_extension}"
        img_name = get_unique_filename(dir_title, img_name)

        image_element2 = driver.find_element("xpath", "//*[@id='photo']")

        try:
            fullsize_link = image_element2.find_element("xpath", "//*[@id='photo-download']")
            fullsize_img_url = fullsize_link.get_attribute("href")

            img_response = requests.get(fullsize_img_url)
            
            # Determine the image format based on Content-Type header
            content_type = img_response.headers.get("Content-Type")
            extension = mimetypes.guess_extension(content_type)
            img_extension = extension if extension else ".jpg"

            img_name = f"{sanitized_img_title}{img_extension}"
            img_name = get_unique_filename(dir_title, img_name)

            os.makedirs(dir_title, exist_ok=True)

            img_path = os.path.join(dir_title, img_name)

            print(f"Full path: {img_path}")
            with open(img_path, "wb") as img_file:
                img_file.write(img_response.content)
                print(f"Downloaded: {img_name}")

            images_processed += 1

            image_element2.click()
            time.sleep(1)

        except StaleElementReferenceException:
            print("Fullsize link is stale, skipping this image.")

    except StaleElementReferenceException:
        print("Image element is stale, skipping this image.")


driver.quit()

print("Image scraping completed.")