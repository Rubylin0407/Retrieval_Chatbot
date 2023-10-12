import pymongo
from dotenv import load_dotenv
import os
from database import get_db_connection, close_mongodb_connection

load_dotenv()

# Use the absolute path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

collection_name = "cola_raw_data"
# Specify the collection to query
fetch_url_collection = get_db_connection()[collection_name]

# perform the query: find all
documents_url = fetch_url_collection.find({})

def query_and_save_data_to_file(collection, file_name):
    try:
        data = list(collection.find())  # Fetch all data from the collection
        with open(file_name, 'w') as file:
            for item in data:
                file.write(f"{str(item)}\n")
        print(f"Data successfully saved to {file_name}")
    except Exception as e:
        print(f"Failed to query and save data: {str(e)}")

if __name__ == "__main__":
    collection = get_db_connection()[collection_name]
    file_name = "data/knowledge.txt"
    query_and_save_data_to_file(collection, file_name)

# Close the MongoDB connection
close_mongodb_connection()
