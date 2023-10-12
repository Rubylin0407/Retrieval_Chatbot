import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from urllib.parse import urljoin
from crawler.database import get_db_connection, insert_unique_url_into_mongodb, close_mongodb_connection

load_dotenv()

data_db_name = os.getenv("DATA_DB_NAME")
collection_cola = get_db_connection(data_db_name)["cola_raw_url"]

def crawl_cola():
    base_url = "https://www.colatour.com.tw/C000_Portal/C000_HP01A_Main.aspx?TourArea=A"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = soup.find_all('a', href=True)

    # Use a set to store unique URLs temporarily
    unique_urls = set()

    for link in links:
        href = link['href']
        absolute_url = urljoin(base_url, href)  # Make the URL absolute
        if "https://www.colatour.com.tw/C10A_TourSell/C10A16_TourItinerary.aspx?PatternNo=" in absolute_url:
            unique_urls.add(absolute_url)

    # Convert the set to a list
    product_urls = [{'url': url} for url in unique_urls]

    return product_urls

# crawl data from cola
crawled_data = crawl_cola() 
# insert data from crawler into mongodb
insert_unique_url_into_mongodb(crawled_data, collection_cola)

# Close the MongoDB connection
close_mongodb_connection()
