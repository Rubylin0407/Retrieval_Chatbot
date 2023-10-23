from flask import Flask, render_template,jsonify,request, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from dotenv import load_dotenv
import logging

import datetime
from flask_jwt_extended import JWTManager
load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("secret_key")

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_secret_key")
jwt = JWTManager()
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
jwt.init_app(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

from server.controllers import chatbot_controller, user_controller