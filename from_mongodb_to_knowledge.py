from dotenv import load_dotenv
import os
from database import get_db_connection, close_mongodb_connection

load_dotenv()

data_db_name = os.getenv("DATA_DB_NAME")

# Use the absolute path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

def query_and_save_data_to_file(collection, file_name, mode='w'):
    try:
        # perform the query: find all
        cursor_object = collection.find({}) # Fetch all data from the collection
        with open(file_name, mode) as file:
            for item in cursor_object:
                # Remove the _id field from the document
                item.pop('_id', None)
                item.pop('insert_time', None)

                # Convert items to a string representation
                item_string = " ".join(str(value) for key, value in item.items())
                file.write(item_string)
                file.write("\n")  # Separate each document with a blank line
        print(f"Data from {collection} successfully appended to {file_name}")
    except Exception as e:
        print(f"Failed to query and save data: {str(e)}")

if __name__ == "__main__":
    # Specify the collections to query
    collection_names = ["cola_raw_data", "cola_raw_data_europe", "cola_raw_data_korea", "cola_raw_data_thailand"]
    file_name = "data/knowledge.txt"
    
    # Clear the file if it exists
    open(file_name, 'w').close()

    db = get_db_connection(data_db_name)
    for collection_name in collection_names:
        fetch_collection = db[collection_name]
        query_and_save_data_to_file(fetch_collection, file_name, mode='a')

    # Close the MongoDB connection
    close_mongodb_connection()
