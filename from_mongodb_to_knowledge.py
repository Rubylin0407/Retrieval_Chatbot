from dotenv import load_dotenv
import os
from crawler.database import get_db_connection, close_mongodb_connection

load_dotenv()

# Use the absolute path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

def query_and_save_data_to_file(collection, file_name):
    try:
        # perform the query: find all
        cursor_object = collection.find({}) # Fetch all data from the collection
        #print(cursor_object)
        with open(file_name, 'w') as file:
            for item in cursor_object:
                # Remove the _id field from the document
                item.pop('_id', None)

                for key, value in item.items():
                    file.write(f"{key}: {value[:500]}")
                file.write("\n")  # Separate each document with a blank line
        print(f"Data successfully saved to {file_name}")
    except Exception as e:
        print(f"Failed to query and save data: {str(e)}")

if __name__ == "__main__":
    # Specify the collection to query
    collection_name = "cola_raw_data"
    fetch_collection = get_db_connection()[collection_name]
    file_name = "data/knowledge.txt"
    query_and_save_data_to_file(fetch_collection, file_name)

# Close the MongoDB connection
close_mongodb_connection()

