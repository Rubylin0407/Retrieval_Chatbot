import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
import os
from crawler.database import db_connection, insert_into_mongodb, close_mongodb_connection

load_dotenv()
sys.setrecursionlimit(1000000)

collection_agoda_name = os.getenv("COLLECTION_AGODA")
collection_agoda = db_connection[collection_agoda_name]

def crawl_agoda():
    response = requests.get("https://www.callingtaiwan.com.tw/agoda-discount-code/")
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the h3 elements
    h3_elements = soup.find_all('h3')

    # Initialize an empty dictionary to store the data
    data = {}

    # Iterate through each h3 element
    for h3 in h3_elements:
        # Get the text of the h3 element
        h3_text = h3.get_text(strip=True)
        # Find the first ul tag after the h3 tag
        ul_elements = h3.find_next('ul')
        # Find all the sibling li elements following this ul
        li_elements = ul_elements.find_all('li')
        
        # Iterate through li elements
        for li in li_elements:
            li_text = li.get_text(strip=True)
            # Check if li_text contains "前往活動連結" or "前往查看"
            if "前往活動連結" in li_text or "前往查看" in li_text:
                # Find the first anchor (a) tag within the li
                anchor = li.find('a')
                if anchor:
                    # Extract the href attribute and append it to the li_text
                    href = anchor.get('href')
                    li_text += f" ({href})"
            
            # Append the modified li_text to the data dictionary
            if h3_text in data:
                data[h3_text].append(li_text)
            else:
                data[h3_text] = [li_text]
    return data

crawled_data = crawl_agoda() 
insert_into_mongodb(crawled_data, collection_agoda)

# Close the MongoDB connection
close_mongodb_connection()