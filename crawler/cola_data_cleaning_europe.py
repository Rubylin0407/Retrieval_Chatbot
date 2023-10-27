from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from chromedriver_py import binary_path 
import os
from server.models.user_model import get_db_connection, insert_data_into_mongodb, close_mongodb_connection
from datetime import datetime
import logging
import pytz

load_dotenv()

# Use the absolute path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

data_db_name = os.getenv("DATA_DB_NAME")

# Initialize the Selenium WebDriver
options = Options()
options.add_argument('--headless')
# Modify this line to use the chromedriver_py binary path
driver = webdriver.Chrome(service=ChromeService(executable_path=binary_path), options=options)

# Specify the collection to query
fetch_url_collection = get_db_connection(data_db_name)["cola_raw_url_europe"]

# Specify the collection to insert
insert_url_collection = get_db_connection(data_db_name)["cola_raw_data_europe"]

# perform the query: find all
documents_url = fetch_url_collection.find({})

# Define the UTC+8 timezone
tz_utc_8 = pytz.timezone('Asia/Taipei')

# documents_url = [{'url':'https://www.colatour.com.tw/C10A_TourSell/C10A16_TourItinerary.aspx?PatternNo=213157'}]
def get_data_from_each_page_cola():
    data_from_urls = []
    urls_no_longer_exist = []
    # Loop through the results and print them
    for document in documents_url:
        # Navigate to the web page
        # ex: driver.get('https://www.colatour.com.tw/C10A_TourSell/C10A16_TourItinerary.aspx?PatternNo=213465')
        driver.get(document["url"])

        try:
            # Click the button "行程概要"
            btn_summary = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "行程概要")]'))
            )
            btn_summary.click()

            # Get tour destinations information
            features = driver.execute_script("return document.querySelector('.mdataInfo-sightBox').textContent;")

            # # Remove newline characters (\n) from the text and replace them with spaces
            features = features.replace('\n', ' ')

            # Locate the main title
            main_title = driver.find_element(By.CSS_SELECTOR, '.tourtit-mdataTitle').text
            
            # Locate each trip's data
            trips = driver.find_elements(By.CSS_SELECTOR, '.dateSmonth-tour')
            trip_data_list = []

            for trip in trips:
                date_data = trip.find_elements(By.CSS_SELECTOR, '.dateSmonth-date')
                price_data = trip.find_elements(By.CSS_SELECTOR, '.dateSmonth-price')
                seat_data = trip.find_elements(By.CSS_SELECTOR, '.dateSmonth-seat')
                
                # Assuming each of the above contains the same number of elements
                for i in range(len(date_data)):
                    if date_data[i].text == "" and price_data[i].text == "" and seat_data[i].text == "":
                        continue
                    trip_info = {
                        "出發日期": date_data[i].text,
                        "行程價格": price_data[i].text,
                        "剩餘位子": seat_data[i].text
                    }
                    trip_data_list.append(trip_info)
            
            page_data = {
                "網址": document["url"],
                "團名": main_title,
                "國家": "歐洲",
                "行程內容": features,
                "行程": trip_data_list,
                'insert_time': datetime.now(tz_utc_8)
            }

            insert_url_collection.insert_one(page_data)

        except Exception as e:
            urls_no_longer_exist.append(document["url"])
            print(f"An error occurred: {e}")

    # close the WebDriver
    driver.quit()

    return data_from_urls, urls_no_longer_exist

insert_url_collection.delete_many({})
lst_of_dic_data, lst_of_url_to_be_deleted = get_data_from_each_page_cola()

# insert data into mongodb
if len(lst_of_dic_data) != 0:
    insert_data_into_mongodb(lst_of_dic_data, insert_url_collection)

# Delete documents with matching URLs
if len(lst_of_url_to_be_deleted) != 0:
    for url in lst_of_url_to_be_deleted:
        fetch_url_collection.delete_many({"url": url})

# Close the MongoDB connection
close_mongodb_connection()
