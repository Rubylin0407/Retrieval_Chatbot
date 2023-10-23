import os
import pymongo
# from pymongo import MongoClient
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure the logging module
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class MongoDBConnector:
    def __init__(self, database_name, collection_name):
        self.mongo_url = os.getenv("MONGODB_URL")
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
    
    def get_collection(self):
        return self.collection

    def insert_one(self, document):
        """
        Inserts a single document into the collection.

        :param document: The document to be inserted.
        """
        try:
            self.collection.insert_one(document)
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to insert document: {e}")