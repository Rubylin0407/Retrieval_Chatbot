from flask import Flask, render_template,jsonify,request, session
from flask_cors import CORS
import openai, os
from dotenv import load_dotenv
import opencc
import mdtex2html
import gradio as gr
from dotenv import load_dotenv
from utils import (
    read_and_process_knowledge_to_langchain_docs,
    initial_langchain_embeddings,
    initial_or_read_langchain_database_faiss,
)

import datetime
from flask_jwt_extended import JWTManager
import hashlib
from database import (get_db_connection, close_mongodb_connection, user_exists, create_user, get_qa_history_from_mongodb,
    insert_fav, delete_fav, get_favorites_from_mongodb)
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
model_kwargs = {'device': 'cpu'}
docs = read_and_process_knowledge_to_langchain_docs("data/knowledge.txt", separator = '\n', chunk_size=1028)
embedding_function = initial_langchain_embeddings("moka-ai/m3e-base", model_kwargs, False)
vectordb = initial_or_read_langchain_database_faiss(docs, embedding_function, "vectordb/vectordbPrivate", False) # not renew vector database
s2t = opencc.OpenCC('s2t.json')

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("secret_key")

user_db_name = os.getenv("USER_DB_NAME")
users_collection = get_db_connection(user_db_name)["user_info"]
QA_history_collection = get_db_connection(user_db_name)["QA_history"]

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_secret_key")
jwt = JWTManager()
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
jwt.init_app(app)

def postprocess(self, y):
    if y is None:
        return []
    for i, (message, response) in enumerate(y):
        y[i] = (
            None if message is None else mdtex2html.convert((message)),
            None if response is None else mdtex2html.convert(response),
        )
    return y

def messeage_prepare(system_info, prompt_info):
        message = [
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt_info}
            ]
        return message
    
def predict(user_input, chatbot):
    # Your prediction logic here
    system_info = "你是聊天機器人 Retrieval Bot, [檢索資料]是由 Ruby Lin 提供的。 當[問題]包含價格時，搜尋$。參考[檢索資料]使用中文簡潔和專業的回覆顧客的[問題], 如果答案不在資料中, 請說 “對不起, 我所擁有的資料中沒有相關資訊, 請您換個問題或將問題描述得更詳細, 讓我能正確完整的回答您”\n\n"
    docs_and_scores_list = vectordb.similarity_search_with_score([user_input], k=2)[0]
    knowledge = "\n".join([docs_and_scores[0].page_content for docs_and_scores in docs_and_scores_list])
    prompt_info =  "[檢索資料]\n{}\n[問題]\n{}".format(knowledge, user_input)
    chatbot.append(user_input)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messeage_prepare(system_info, prompt_info),
        temperature = 0.1,
    )
    print(f"response:{response}")
    chatbot[-1] = (response["choices"][0]["message"]["content"])
    return chatbot

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/searchhistory', methods=['GET']) 
def search_history():     
    return render_template('searchhistory.html')

@app.route('/api/get-qa-history')
def get_qa_history():
    try:
        if session.get('logged_in'):
            email = session.get('email')
            user_data = get_qa_history_from_mongodb(email, QA_history_collection)
            # Check if user_data is not []
            if len(user_data) !=0:
                print(user_data)
                return jsonify(user_data)
            else:
                return jsonify([])  # Return an empty array if user_data is None
        else:
            return jsonify({"error": "User not logged in"})
    except Exception as e:
        print(f"Failed to fetch data from QA_history_collection: {str(e)}")
        return jsonify({"error": "Failed to fetch QA history"})

@app.route('/api/get-user-favorites')
def get_fav():
    try:
        if session.get('logged_in'):
            email = session.get('email')
            fav_collection = get_db_connection(user_db_name)["favorites"]
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
        print(f"Failed to check data from {fav_collection.name}: {str(e)}")
        return jsonify([])  # Handle the error gracefully with an empty JSON array

@app.route('/api/add-favorite', methods = ['POST'])
def add_favorite():
    try:
        data = request.get_json()
        QA_pair_id = data.get('QA_pair_id')

        # The rest of your code to add the favorite goes here
        email = session.get('email')
        insert_fav(email, QA_pair_id)
        
        # Return a response indicating success if needed
        return jsonify({'message': 'Favorite added successfully'})
    except Exception as e:
        print(f"Failed to add favorite: {str(e)}")
        # Handle errors and return an appropriate response
        return jsonify({'error': 'Failed to add favorite'}), 500  # HTTP status code 500 for internal server error

@app.route('/api/remove-favorite', methods = ['POST'])
def remove_favorite():
    try:
        data = request.get_json()
        QA_pair_id = data.get('QA_pair_id')

        # The rest of your code to add the favorite goes here
        email = session.get('email')
        delete_fav(email, QA_pair_id)
        
        # Return a response indicating success if needed
        return jsonify({'message': 'Favorite removed successfully'})
    except Exception as e:
        print(f"Failed to remove favorite: {str(e)}")
        # Handle errors and return an appropriate response
        return jsonify({'error': 'Failed to remove favorite'}), 500  # HTTP status code 500 for internal server error

@app.route('/favorites', methods=['GET']) 
def favorites():     
    return render_template('favorites.html')

@app.route('/api/get-favorites')
def get_favorites():
    try:
        if session.get('logged_in'):
            email = session.get('email')
            fav_lst = get_favorites_from_mongodb(email)
            # Always return a valid JSON response
            return jsonify(fav_lst)

    except Exception as e:
        print(f"Failed to check data to favorites page: {str(e)}")
        return jsonify([])  # Handle the error gracefully with an empty JSON array
        
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.get_json().get('data')
        chatbot = []  # Initialize an empty chatbot conversation

        # Get the chatbot response
        response = predict(user_input, chatbot)
        print(f"predict_response:{response}")
        if session['logged_in'] == True:
            QA_pair = {
                    "email": session['email'],
                    "question": user_input,
                    "answer": response
                }
            # insert user's question and chatbot's response into mongodb
            QA_history_collection.insert_one(QA_pair)
        return jsonify({"response": True, "message": response})
    except Exception as e:
        print(e)
        error_message = f'Error: {str(e)}'
        return jsonify({"message":error_message,"response":False})

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
                return jsonify({"error": "Name, email, and password are required."}), 400
            
            if user_exists(email, users_collection):
                return jsonify({"error": "Email already exists."}), 403
            
            # Store user information in MongoDB
            create_user(name, email, password, provider, users_collection)   
            return render_template('login.html')
        except Exception as e:
            print(f"Error when signing up: {str(e)}")
            return jsonify("An error occurred while signing up."), 500

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
            user_data = user_exists(email, users_collection)
            # print(user_data)
            if provider == "native":
                # Hash the provided password and compare it with the stored password
                provided_password_hash = hashlib.sha256(password.encode()).hexdigest()
                stored_password = user_data["password"]
                if provided_password_hash != stored_password:
                    return jsonify({"Wrong password"}), 403
                else: 
                    session['logged_in'] = True
                    session['name'] = user_data["name"]
                    session['email'] = user_data["email"]
                    print("Successfully logging in")
            return render_template('index.html')
        except Exception as e:
            print(f"Error when logging in: {str(e)}")
            return jsonify("An error occurred while logging in."), 500

@app.route('/user/logout')
def logout():
    session.pop('logged_in', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)