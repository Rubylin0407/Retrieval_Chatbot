from flask import render_template,jsonify,request, session
import os
from dotenv import load_dotenv
import logging

from server import app
from server.models.mongodb import MongoDBConnector
import hashlib
from server.models.user_model import (close_mongodb_connection, user_exists, create_user, get_qa_history_from_mongodb,
    insert_fav, delete_fav, get_favorites_from_mongodb)
load_dotenv()

user_db_name = os.getenv("USER_DB_NAME")
user_info_collection = MongoDBConnector(user_db_name, "user_info")
QA_history_collection = MongoDBConnector(user_db_name, "QA_history")
fav_collection = MongoDBConnector(user_db_name, "favorites")      

@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        try:
            provider = "native"
            data = request.form

            name, email, password = data.get('name'), data.get('email'), data.get('password')
            
            if not all([name, email, password]):
                return "Name, email, and password are required.", 400
            
            if user_exists(email, user_info_collection):
                return "Email already exists.", 403
            
            # Store user information in MongoDB
            create_user(name, email, password, provider, user_info_collection)   
            return render_template('login.html')
        except Exception as e:
            logging.error(f"Error when signing up: {str(e)}")
            return "An error occurred while signing up.", 500

@app.route('/user/login', methods=['GET', 'POST'])
def user_sign_in():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        try:
            data = request.form
            provider = "native"
            email, password = data.get('email'), data.get('password')
            
            if not all([email, password, provider]):
                return jsonify("Email and password are required."), 400
            # if user exist, return user_information, including user name, email and hashed password
            user_data = user_exists(email, user_info_collection)
            if provider == "native":
                # Hash the provided password and compare it with the stored password
                provided_password_hash = hashlib.sha256(password.encode()).hexdigest()
                stored_password = user_data["password"]
                if provided_password_hash != stored_password:
                    return "Wrong password.", 403
                else: 
                    session['logged_in'] = True
                    session['name'] = user_data["name"]
                    session['email'] = user_data["email"]
                    logging.info(f"Successfully logging in: {session['email']}")
            return render_template('index.html')
        except Exception as e:
            logging.error(f"Error when logging in: {str(e)}")
            return "An error occurred while logging in.", 500

@app.route('/user/logout')
def logout():
    session.pop('logged_in', None)
    return render_template('index.html')

@app.route('/searchhistory', methods=['GET']) 
def search_history():
    try:
        if session.get('logged_in', False) == True:
            return render_template('searchhistory.html')
        else:
            return render_template('login.html')
    except Exception as e:
        logging.error(f"Error when fetching search history page: {str(e)}")
        return jsonify({"error": "Failed to fetch QA history"})

@app.route('/api/v1/get-qa-history')
def get_qa_history():
    try:
        if session.get('logged_in', False) == True:
            email = session.get('email')
            user_data = get_qa_history_from_mongodb(email, QA_history_collection)
            # Check if user_data is not []
            if len(user_data) !=0:
                logging.info(user_data)
                return jsonify(user_data)
            else:
                return jsonify([])  # Return an empty array if user_data is None
        else:
            return jsonify({"error": "User not logged in"})
    except Exception as e:
        logging.error(f"Failed to fetch data from QA_history_collection: {str(e)}")
        return jsonify({"error": "Failed to fetch QA history"})

@app.route('/api/v1/get-user-favorites')
def get_fav():
    try:
        if session.get('logged_in', False) == True:
            email = session.get('email')
            # Query MongoDB for all documents with the specified email
            cursor = fav_collection.find({"email": email})

            # Initialize an empty list to store question and answer pairs
            fav_lst = []

            # Iterate through the cursor and extract 'question' and 'answer' from each document
            for doc in cursor:
                id_str = str(doc['QA_pair_id'])
                if 'email' in doc:
                    fav_lst.append({
                        'QA_pair_id': id_str
                    })
            # Always return a valid JSON response
            return jsonify(fav_lst)

    except Exception as e:
        logging.error(f"Failed to check data from {fav_collection}: {str(e)}")
        return jsonify([])  # Handle the error gracefully with an empty JSON array

@app.route('/api/v1/add-favorite', methods = ['POST'])
def add_favorite():
    try:
        data = request.get_json()
        QA_pair_id = data.get('QA_pair_id')
        email = session.get('email')
        insert_fav(email, QA_pair_id, fav_collection)
        
        # Return a response indicating success if needed
        return jsonify({'message': 'Favorite added successfully'})
    except Exception as e:
        logging.error(f"Failed to add favorite: {str(e)}")
        # Handle errors and return an appropriate response
        return jsonify({'error': 'Failed to add favorite'}), 500  # HTTP status code 500 for internal server error

@app.route('/api/v1/remove-favorite', methods = ['POST'])
def remove_favorite():
    try:
        data = request.get_json()
        QA_pair_id = data.get('QA_pair_id')

        # The rest of your code to add the favorite goes here
        email = session.get('email')
        delete_fav(email, QA_pair_id, fav_collection)
        
        # Return a response indicating success if needed
        return jsonify({'message': 'Favorite removed successfully'})
    except Exception as e:
        logging.error(f"Failed to remove favorite: {str(e)}")
        # Handle errors and return an appropriate response
        return jsonify({'error': 'Failed to remove favorite'}), 500  # HTTP status code 500 for internal server error

@app.route('/favorites', methods=['GET']) 
def favorites():     
    try:
        if session.get('logged_in', False) == True:   
            return render_template('favorites.html')
        else:
            return render_template('login.html')
    except Exception as e:
        logging.error(f"Error when fetching search history page: {str(e)}")
        return jsonify({"error": "Failed to fetch QA history"})

@app.route('/api/v1/get-favorites')
def get_favorites():
    try:
        if session.get('logged_in', False) == True:
            email = session.get('email')
            fav_lst = get_favorites_from_mongodb(email, fav_collection, QA_history_collection)
            # Always return a valid JSON response
            return jsonify(fav_lst)

    except Exception as e:
        logging.error(f"Failed to check data to favorites page: {str(e)}")
        return jsonify([])  # Handle the error gracefully with an empty JSON array