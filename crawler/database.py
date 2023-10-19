import os
import pymongo
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
import hashlib
load_dotenv()

# MongoDB connection details
mongo_url = os.getenv("MONGODB_URL")
# data_db_name = os.getenv("DATA_DB_NAME")
# user_db_name = os.getenv("USER_DB_NAME")

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
    for url in urls:
        # Check if the URL already exists in the collection
        existing_url = collection.find_one({'url': url['url']})
        if existing_url is None:
            # URL doesn't exist in the collection, insert it
            collection.insert_one(url)
            print(f"Inserted URL: {url['url']} into {collection.name}")
        # else: not insert, because URL already exists in the collection

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

def check_validation(password, password_jwt, collection):
    user = collection.find_one({"password": password_jwt})
    if user:
        hashed_password = "pbkdf2:sha256:600000$" + user["password"]
        return check_password_hash(hashed_password, password)
    return False

# Close the MongoDB connection
def close_mongodb_connection():
    client.close()
