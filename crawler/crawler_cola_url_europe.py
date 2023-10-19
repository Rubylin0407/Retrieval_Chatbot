import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from urllib.parse import urljoin
from database import get_db_connection, insert_unique_url_into_mongodb, close_mongodb_connection
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

data_db_name = os.getenv("DATA_DB_NAME")
collection_cola = get_db_connection(data_db_name)["cola_raw_url_europe"]

def crawl_cola():
    base_url = "https://www.colatour.com.tw/C000_Portal/C000_HP01A_Main.aspx?TourArea=L"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch URL {base_url}: {str(e)}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all('a', href=True)
    unique_urls = set()

    for link in links:
        href = link['href']
        absolute_url = urljoin(base_url, href)
        if "https://www.colatour.com.tw/C10A_TourSell/C10A16_TourItinerary.aspx?PatternNo=" in absolute_url:
            unique_urls.add(absolute_url)
        
        # time.sleep(1)  # be polite to the server
    
    product_urls = [{'url': url} for url in unique_urls]
    return product_urls

# crawl data from cola
crawled_data = crawl_cola() 
# insert data from crawler into mongodb
insert_unique_url_into_mongodb(crawled_data, collection_cola)

# Close the MongoDB connection
close_mongodb_connection()
