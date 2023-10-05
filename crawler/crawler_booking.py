import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
import os
from crawler.database import db_connection, insert_into_mongodb, close_mongodb_connection

load_dotenv()
sys.setrecursionlimit(1000000)

collection_booking_name = os.getenv("COLLECTION_BOOKING")
collection_booking = db_connection[collection_booking_name]

def crawler_booking():
    response = requests.get("https://www.callingtaiwan.com.tw/booking-com-code/")
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the h3 elements
    h1_elements = soup.find_all('h1')

    # Initialize an empty dictionary to store the data
    data = {}

    # Iterate through each h3 element
    for h1 in h1_elements:
        # Get the text of the h3 element
        h1_text = h1.get_text(strip=True)
        # Find the first ul tag after the h3 tag
        ul_elements = h1.find_next('ul')
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
            if h1_text in data:
                data[h1_text].append(li_text)
            else:
                data[h1_text] = [li_text]

    # Find all <h2> elements
    h2_element = soup.find('h2')

    brand_name = h2_element.text.strip()

    data[brand_name] = []

    # Find the next <table> element (coupon details)
    table = h2_element.find_next('table')
    if table:
        # Find all rows in the table except the header row
        validity_text = table.find_all('tr')[0].find('td').text.strip()
        rows = table.find_all('tr')[1:]
        for row in rows:
            columns = row.find_all('td')
            validity = columns[0].text.strip()
            content = columns[1].text.strip()
            coupon_code = columns[2].text.strip()
            # Check if columns[2] contains an <a> tag
            coupon_link = columns[2].find('a')
            if coupon_link:
                coupon_url = coupon_link.get('href').strip()
            else:
                coupon_url = ""
            
            # Append all data together for this brand
            brand_data = ''
            brand_data = validity_text+validity+" "+content+coupon_code+coupon_url
            data[brand_name].append(brand_data)
                        
    return(data)

crawled_data = crawler_booking() 
insert_into_mongodb(crawled_data, collection_booking)
# Close the MongoDB connection
close_mongodb_connection()