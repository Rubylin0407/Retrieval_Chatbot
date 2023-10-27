import os
import pymongo
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
    
    def find(self, query=None, **kwargs):
        """
        Retrieves documents from the collection based on a query.

        :param query: A dictionary specifying the search criteria.
        :param kwargs: Additional arguments to pass to the find method (e.g., sort, limit).
        :return: A cursor to the results.
        """
        try:
            return self.collection.find(query, **kwargs)
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to fetch documents: {e}")
            return []
    def find_one(self, query=None, **kwargs):
        """
        Retrieves a single document from the collection based on a query.

        :param query: A dictionary specifying the search criteria.
        :param kwargs: Additional arguments to pass to the find_one method (e.g., projection).
        :return: A single document or None.
        """
        try:
            return self.collection.find_one(query, **kwargs)
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to fetch document: {e}")
            return None

    def delete_one(self, query):
        """
        Deletes a single document from the collection based on a query.

        :param query: A dictionary specifying the search criteria for deletion.
        :return: The result of the deletion operation (includes info like number of documents deleted).
        """
        try:
            return self.collection.delete_one(query)
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to delete document: {e}")
            return None