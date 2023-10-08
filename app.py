from flask import Flask, render_template,jsonify,request
from flask_cors import CORS
import requests, openai, os
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

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
model_kwargs = {'device': 'cpu'}
docs = read_and_process_knowledge_to_langchain_docs("data/knowledge.txt", separator = '\n', chunk_size=1028)
embedding_function = initial_langchain_embeddings("moka-ai/m3e-base", model_kwargs, False)
vectordb = initial_or_read_langchain_database_faiss(docs, embedding_function, "vectordb/vectordbPrivate", False) # not renew vector database
s2t = opencc.OpenCC('s2t.json')

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)