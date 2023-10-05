# incomplete
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
import os
from urllib.parse import urljoin
#from database import db_connection, insert_into_mongodb, close_mongodb_connection

load_dotenv()
sys.setrecursionlimit(1000000)

# collection_agoda_name = os.getenv("COLLECTION_AGODA")
# collection_agoda = db_connection[collection_agoda_name]

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 設置Chrome選項以啟用Headless模式（可選）
chrome_options = Options()
chrome_options.add_argument("--headless")

# 指定Chrome Driver的路徑
driver_path = "/path/to/chromedriver"

# 創建一個Chrome瀏覽器實例，並傳入Chrome選項
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 訪問目標網頁
url = "https://search.liontravel.com/zh-tw/%E5%A4%A7%E9%98%AA,%E6%9D%B1%E4%BA%AC,%E5%8C%97%E6%B5%B7%E9%81%93,%E6%B2%96%E7%B9%A9?"
driver.get(url)

# 使用Selenium的find_elements方法來查找所有符合條件的<div>元素
search_results = driver.find_elements(By.XPATH, "//div[@class='search_result']")

# 遍歷所有找到的<div>元素並提取其文本內容
for result in search_results:
    print(result.text)

# 關閉瀏覽器
driver.quit()


# 訪問網站
driver.get(url)


# def crawl_lion():
#     base_url = "https://search.liontravel.com/zh-tw/%E5%A4%A7%E9%98%AA,%E6%9D%B1%E4%BA%AC,%E5%8C%97%E6%B5%B7%E9%81%93,%E6%B2%96%E7%B9%A9?"
#     response = requests.get(base_url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     print(soup)

#     links = soup.select(".search_result")
#     print(links)
#     #links = soup.find_all('a', href=True)
#     # Extract and filter the href attribute from each <a> tag
#     product_urls = []

#     for link in links:
#         print(link)
#         href = link['href']
#         absolute_url = urljoin(base_url, href)  # Make the URL absolute
#         #if "https://www.colatour.com.tw/C10A_TourSell/C10A16_TourItinerary.aspx?PatternNo=" in absolute_url:
#         product_urls.append(absolute_url)

#     # # Print the product URLs
#     # for url in product_urls:
#     #     print(url)

# crawl_lion()