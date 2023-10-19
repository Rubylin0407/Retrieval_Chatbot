import os
import pymongo
from dotenv import load_dotenv
from datetime import datetime
import logging
import pytz
from datetime import datetime

logging.basicConfig(level=logging.INFO)

load_dotenv()

# Define the UTC+8 timezone
tz_utc_8 = pytz.timezone('Asia/Taipei')

# MongoDB connection details
mongo_url = os.getenv("MONGODB_URL")

client = pymongo.MongoClient(mongo_url)

def get_db_connection(database_name):
    # Connect to MongoDB
    db = client[database_name]
    return db

def insert_data_into_mongodb(crawled_data, collection):
    try:
        with client.start_session() as session:
            collection.insert_many(crawled_data)
        print(f"Successfully inserted data into {collection.name}")
    except Exception as e:
        print(f"Failed to insert data into {collection.name}: {str(e)}")

def insert_unique_url_into_mongodb(urls, collection):
    # Delete all documents in the collection
    collection.delete_many({})

    # Insert new data
    for url in urls:
        # Include the current time as the insert time
        url_with_time = {
            'url': url['url'],
            'insert_time': datetime.now(tz_utc_8)
        }
        
        try:
            collection.insert_one(url_with_time)
            logging.info(f"Inserted URL: {url['url']} into {collection.name} at {url_with_time['insert_time']}")
        except Exception as e:
            logging.error(f"Error while inserting URL {url['url']}: {str(e)}")

# Close the MongoDB connection
def close_mongodb_connection():
    client.close()
