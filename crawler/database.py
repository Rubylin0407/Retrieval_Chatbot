import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection details
mongo_url = os.getenv("MONGODB_URL")
db_name = os.getenv("DB_NAME")
client = pymongo.MongoClient(mongo_url)

def get_db_connection():
    # Connect to MongoDB
    db = client[db_name]
    return db

def insert_crawler_data_into_mongodb(crawled_data, collection):
    try:
        with client.start_session() as session:
            collection.insert_many(crawled_data)
        print(f"Successfully inserted crawler data into {collection.name}")
    except Exception as e:
        print(f"Failed to insert data into {collection.name}: {str(e)}")

def insert_unique_url_into_mongodb(urls, collection):
    for url in urls:
        # Check if the URL already exists in the collection
        existing_url = collection.find_one({'url': url['url']})
        if existing_url is None:
            # URL doesn't exist in the collection, insert it
            collection.insert_one(url)
            print(f"Inserted URL: {url['url']} into {collection.name}")
        # else: not insert, because URL already exists in the collection

# Close the MongoDB connection
def close_mongodb_connection():
    client.close()
