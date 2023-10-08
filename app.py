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
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import hashlib
from crawler.database import get_db_connection, insert_data_into_mongodb, close_mongodb_connection, user_exists, create_user, check_validation
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
    system_info = "你是聊天機器人 Retrieval Bot, [檢索資料]是由 Ruby Lin 提供的。 參考[檢索資料]使用中文簡潔和專業的回覆顧客的[問題], 如果答案不在資料中, 請說 “對不起, 我所擁有的資料中沒有相關資訊, 請您換個問題或將問題描述得更詳細, 讓我能正確完整的回答您”\n\n"
    docs_and_scores_list = vectordb.similarity_search_with_score([user_input], k=5)[0]
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

# Custom function to check if a user is signed in
def is_user_signed_in():
    return 'user_id' in session  # Check if the 'user_id' key is in the session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.get_json().get('data')
        print(user_input)
        chatbot = []  # Initialize an empty chatbot conversation

        # Get the chatbot response
        response = predict(user_input, chatbot)
        print(f"predict_response:{response}")
        print(jsonify({"response": True, "message": response}))

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
            
            user_data = user_exists(email, users_collection)
            print(user_data)
            if provider == "native":
                # stored_password = user_data.get("password", "")
                stored_password = user_data["password"]
                # Hash the provided password and compare it with the stored password
                provided_password_hash = hashlib.sha256(password.encode()).hexdigest()
                if provided_password_hash != stored_password:
                    return jsonify({"Wrong password"}), 403
                else: 
                    session['logged_in'] = True
                    session['username'] = user_data["name"]
                    print("Successfully logging in")
            return render_template('index.html')
        except Exception as e:
            print(f"Error when logging in: {str(e)}")
            return jsonify("An error occurred while logging in."), 500

@app.route('/user/logout/')
def logout():
    session.pop('logged_in', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)