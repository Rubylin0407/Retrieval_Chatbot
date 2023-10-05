from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
from database import get_db_connection, insert_crawler_data_into_mongodb, close_mongodb_connection

load_dotenv()

# Use the absolute path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Initialize the Selenium WebDriver
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Specify the collection to query
fetch_url_collection = get_db_connection()["cola_raw_url"]

# Specify the collection to insert
insert_url_collection = get_db_connection()["cola_raw_data"]

# perform the query: find all
documents_url = fetch_url_collection.find({})

def get_data_from_each_page_cola():
    data_from_urls = []
    urls_no_longer_exist = []
    # Loop through the results and print them
    for document in documents_url:
        #print(url["url"])

        # Navigate to the web page
        # ex: driver.get('https://www.colatour.com.tw/C10A_TourSell/C10A16_TourItinerary.aspx?PatternNo=213465')
        driver.get(document["url"])
        try:
            # Locate the element by its class name
            element = driver.find_element(By.CLASS_NAME, 'mainContainer_itinerary')

            # Remove newline characters (\n) from the text and replace them with spaces
            cleaned_text = element.text.replace('\n', ' ')

            # Check if a document with the same URL already exists in the insert_url_collection
            existing_document = insert_url_collection.find_one({"url": document["url"]})

            if existing_document:
                # Update the existing document with the new data
                insert_url_collection.update_one(
                    {"url": document["url"]},
                    {"$set": {"data": cleaned_text}}
                )
            else:
                # Insert a new document with the URL and data
                insert_url_collection.insert_one({"url": document["url"], "data": cleaned_text})

        except Exception as e:
            urls_no_longer_exist.append(document["url"])
            print(f"An error occurred: {e}")

    # close the WebDriver
    driver.quit()

    return data_from_urls, urls_no_longer_exist

lst_of_dic_data, lst_of_url_to_be_deleted = get_data_from_each_page_cola()

# insert data into mongodb
if len(lst_of_dic_data) != 0:
    insert_crawler_data_into_mongodb(lst_of_dic_data, insert_url_collection)

# Delete documents with matching URLs
if len(lst_of_url_to_be_deleted) != 0:
    for url in lst_of_url_to_be_deleted:
        fetch_url_collection.delete_many({"url": url})

# Close the MongoDB connection
close_mongodb_connection()
