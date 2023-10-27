from dotenv import load_dotenv
import hashlib
from bson import ObjectId
import logging
import pytz
load_dotenv()

tz_utc_8 = pytz.timezone('Asia/Taipei')

def get_favorites_from_mongodb(email, fav_collection, QA_history_collection):
    try:
        # Query MongoDB for all documents with the specified email in favorites collection
        cursor = fav_collection.find({"email": email})
        
        # Initialize an empty list to store question and answer pairs
        qa_pairs_in_fav_collection = []

        # Iterate through the cursor
        for fav_doc in cursor:
            # Find the corresponding QA pair using the QA_pair_id from the favorite document
            qa_doc = QA_history_collection.find_one({"_id": fav_doc['QA_pair_id']})
            if qa_doc:
                qa_pairs_in_fav_collection.append({
                    'QA_pair_id': str(fav_doc['QA_pair_id']),
                    'question': qa_doc['question'],
                    'answer': qa_doc['answer']
                })
        
        return qa_pairs_in_fav_collection

    except Exception as e:
        logging.error(f"Failed to check data from {fav_collection}: {str(e)}")
        return None

def get_qa_history_from_mongodb(email, QA_history_collection):
    try:
        # Query MongoDB for all documents with the specified email
        cursor = QA_history_collection.find({"email": email})
        
        # Initialize an empty list to store question and answer pairs
        qa_pairs = []
        if cursor:
            # Iterate through the cursor and extract 'question' and 'answer' from each document
            for doc in cursor:
                if 'question' in doc and 'answer' in doc:
                    id_str = str(doc['_id'])
                    qa_pairs.append({
                        'id_str': id_str,
                        'question': doc['question'],
                        'answer': doc['answer']
                    })
        return qa_pairs
    except Exception as e:
        logging.error(f"Failed to check data from {QA_history_collection}: {str(e)}")
        return None  # Handle the error gracefully

def insert_fav(email, QA_pair_id, fav_collection):
    try:
        fav_data = {
            "email": email,
            "QA_pair_id": ObjectId(QA_pair_id)
        }
        fav_collection.insert_one(fav_data) 
        logging.info(f"Successfully inserted favorite data into {fav_collection}")
    except Exception as e:
        logging.error(f"Failed to insert favorite data into {fav_collection}: {str(e)}")

def delete_fav(email, QA_pair_id, fav_collection):
    try:
        fav_data = {
            "email": email,
            "QA_pair_id": ObjectId(QA_pair_id),
        }
        fav_collection.delete_one(fav_data) 
        logging.info(f"Successfully deleted favorite data from {fav_collection}")
    except Exception as e:
        logging.error(f"Failed to deleted favorite data from {fav_collection}: {str(e)}")

# check if user already exist in database
def user_exists(email, user_info_collection):
    try:
        user_data = user_info_collection.find_one({"email": email})
        if user_data:
            return user_data
    except Exception as e:
        print(f"Failed to check data from {user_info_collection}: {str(e)}")    

def create_user(name, email, password, provider, user_info_collection):
    try:
        password_jwt = hashlib.sha256(password.encode()).hexdigest()
        user_data = {
            "provider": provider,
            "name": name,
            "email": email,
            "password": password_jwt
        }
        user_info_collection.insert_one(user_data) 
        logging.info(f"Successfully inserted data into {user_info_collection}")
    except Exception as e:
        logging.error(f"Failed to insert data into {user_info_collection}: {str(e)}")

# Close the MongoDB connection
def close_mongodb_connection(collection):
    collection.close()
