import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
import os
from database import db_connection, insert_into_mongodb, close_mongodb_connection

load_dotenv()
sys.setrecursionlimit(1000000)

collection_foodpanda_ubereats_name = os.getenv("COLLECTION_FOODPANDA_UBEREATS")
collection_foodpanda_ubereats = db_connection[collection_foodpanda_ubereats_name]

def crawl_foodpanda_ubereats():
    response = requests.get(
        "https://www.callingtaiwan.com.tw/外送優惠總整理-foodpanda-ubereats/")
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <h2> elements
    h2_elements = soup.find_all('h2')

    # Initialize empty lists to store data
    data = {}

    for h2_element in h2_elements:
        # Extract the text within the <a> element within <h2> (food delivery brand name)
        brand_name = h2_element.find('a', attrs={'rel': 'noopener noreferrer'})
        if brand_name:
            brand_name = brand_name.text.strip().split(' ')[0]
            data[brand_name] = []

            # Find the next <table> element (coupon details)
            table = h2_element.find_next('table', id='coupon_table')
            if table:
                # Find all rows in the table except the header row
                rows = table.find_all('tr')[1:]
                for row in rows:
                    columns = row.find_all('td')
                    validity = columns[0].text.strip()
                    content = columns[1].text.strip()
                    coupon_code = columns[2].text.strip().split('\n')[0]
                    coupon_url = columns[2].find('a')['href'].strip()
                    
                    # Append all data together for this brand
                    brand_data = ''
                    brand_data = validity+content+coupon_code+coupon_url
                    data[brand_name].append(brand_data)
    return data

# Crawl data and store it in MongoDB
crawled_data = crawl_foodpanda_ubereats() 
insert_into_mongodb(crawled_data, collection_foodpanda_ubereats)

# Close the MongoDB connection
close_mongodb_connection()