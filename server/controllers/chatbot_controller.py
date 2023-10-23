from flask import render_template,jsonify,request, session
import openai, os
from dotenv import load_dotenv
import opencc
import logging
from data_pipeline.utils import (
    read_and_process_knowledge_to_langchain_docs,
    initial_langchain_embeddings,
    initial_or_read_langchain_database_faiss,
)
from server import app
from server.models.mongodb import MongoDBConnector

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
model_kwargs = {'device': 'cpu'}
docs = read_and_process_knowledge_to_langchain_docs("data_pipeline/data/knowledge.txt", separator = '\n', chunk_size=1)
embedding_function = initial_langchain_embeddings("moka-ai/m3e-base", model_kwargs, False)
vectordb = initial_or_read_langchain_database_faiss(docs, embedding_function, "data_pipeline/vectordb/vectordbPrivate", False) # not renew vector database
s2t = opencc.OpenCC('s2t.json')

user_db_name = os.getenv("USER_DB_NAME")
QA_history_collection = MongoDBConnector(user_db_name, "QA_history")

def messeage_prepare(system_info, user_input, history=[]):
    message = [{"role": "system", "content": system_info}]
    if len(history) > 0:
        for old_question, old_answer in history:
            message.append({"role": "user", "content": old_question})
            message.append({"role": "assistant", "content": old_answer})

    message.append({"role": "user", "content": user_input})
    return message
    
def predict(user_input, history, system_info):
    # Your prediction logic here
    if len(history) == 0:
        docs_and_scores_list = vectordb.similarity_search_with_score([user_input], k=4)[0]
        knowledge = "\n".join([docs_and_scores[0].page_content for docs_and_scores in docs_and_scores_list])
        system_info += "[檢索資料]\n{}\n".format(knowledge)
        logging.info(f"knowledge:{knowledge}")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages = messeage_prepare(system_info, user_input, history),
        temperature = 0.01,
    )
    logging.info(f"history :{history}\nsystem_info:{system_info}")
    response = s2t.convert(response["choices"][0]["message"]["content"])

    return response, system_info

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the chatbot response
        user_input = request.get_json().get('data')
        history = request.get_json().get('qa_history')
        system_info = request.get_json().get('system_info')
        response, system_info = predict(user_input, history, system_info)
        history.append((user_input, response))

        logging.info(f"predict_response:{response}")
        if session.get('logged_in', False) == True:
            QA_pair = {
                    "email": session['email'],
                    "question": user_input,
                    "answer": response
                }
            # insert user's question and chatbot's response into mongodb
            QA_history_collection.insert_one(QA_pair)
        
        # return the JSON string
        return jsonify({"response": True, "message": response, "qa_history": history, "system_info":system_info})

    except Exception as e:
        logging.error(e)
        error_message = f'Error: {str(e)}'
        return jsonify({"message":error_message,"response":False})