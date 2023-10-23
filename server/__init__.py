from flask import Flask, render_template,jsonify,request, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from dotenv import load_dotenv

import datetime
from flask_jwt_extended import JWTManager
# from server.models.database import (get_db_connection, close_mongodb_connection, user_exists, create_user, get_qa_history_from_mongodb,
#     insert_fav, delete_fav, get_favorites_from_mongodb)
load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("secret_key")

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_secret_key")
jwt = JWTManager()
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
jwt.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

from server.controllers import chatbot_controller, user_controller