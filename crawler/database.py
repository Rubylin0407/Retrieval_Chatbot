import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection details
mongo_url = os.getenv("MONGODB_URL")
db_name = os.getenv("DB_NAME")
client = pymongo.MongoClient(mongo_url)

def db_connection():
    # Connect to MongoDB
    db = client[db_name]
    return db

def insert_into_mongodb(crawled_data, collection):
    try:
        collection.insert_one(crawled_data)
        print(f"successfully insert crawler data for {collection.name}")
    except Exception as e:
        print(f"Failed to insert data into {collection.name}: {str(e)}")

# Close the MongoDB connection
def close_mongodb_connection():
    client.close()
