import os
import pymongo
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
import hashlib
from bson import json_util
load_dotenv()

# MongoDB connection details
mongo_url = os.getenv("MONGODB_URL")
client = pymongo.MongoClient(mongo_url)

user_db_name = os.getenv("USER_DB_NAME")

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
    for url in urls:
        # Check if the URL already exists in the collection
        existing_url = collection.find_one({'url': url['url']})
        if existing_url is None:
            # URL doesn't exist in the collection, insert it
            collection.insert_one(url)
            print(f"Inserted URL: {url['url']} into {collection.name}")
        # else: not insert, because URL already exists in the collection

def get_qa_history_from_mongodb(email, collection):
    try:
        # Query MongoDB for all documents with the specified email
        cursor = collection.find({"email": email})
        
        # Initialize an empty list to store question and answer pairs
        qa_pairs = []
        if cursor:
            # Iterate through the cursor and extract 'question' and 'answer' from each document
            for doc in cursor:
                # print(doc)
                if 'question' in doc and 'answer' in doc:
                    doc['_id'] = json_util.dumps(doc['_id'])
                    qa_pairs.append({
                        '_id': doc['_id'],
                        'question': doc['question'],
                        'answer': doc['answer']
                    })

        return qa_pairs
    except Exception as e:
        print(f"Failed to check data from {collection.name}: {str(e)}")
        return None  # Handle the error gracefully

def insert_fav(email, QA_pair_id):
    try:
        fav_collection = get_db_connection(user_db_name)["favorites"]
        with client.start_session() as session:
            fav_data = {
                "email": email,
                "QA_pair_id": QA_pair_id,
            }
            fav_collection.insert_one(fav_data) 
            print(f"Successfully inserted favorite data into {fav_collection.name}")
    except Exception as e:
        print(f"Failed to insert favorite data into {fav_collection.name}: {str(e)}")

def delete_fav(email, QA_pair_id):
    try:
        fav_collection = get_db_connection(user_db_name)["favorites"]
        with client.start_session() as session:
            fav_data = {
                "email": email,
                "QA_pair_id": QA_pair_id,
            }
            fav_collection.delete_one(fav_data) 
            print(f"Successfully inserted favorite data into {fav_collection.name}")
    except Exception as e:
        print(f"Failed to insert favorite data into {fav_collection.name}: {str(e)}")

# check if user already exist in database
def user_exists(email, collection):
    try:
        with client.start_session() as session:
            # Query MongoDB for the user with the specified email
            user_data = collection.find_one({"email": email})
            if user_data:
                return user_data
    except Exception as e:
        print(f"Failed to check data from {collection.name}: {str(e)}")    

def create_user(name, email, password, provider, collection):
    try:
        with client.start_session() as session:
            password_jwt = hashlib.sha256(password.encode()).hexdigest()
            user_data = {
                "provider": provider,
                "name": name,
                "email": email,
                "password": password_jwt
            }
            collection.insert_one(user_data) 
            print(f"Successfully inserted data into {collection.name}")
    except Exception as e:
        print(f"Failed to insert data into {collection.name}: {str(e)}")

# Close the MongoDB connection
def close_mongodb_connection():
    client.close()
