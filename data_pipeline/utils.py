import os
import openai
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from data_pipeline.vectorstores import FAISS
from data_pipeline.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings

def read_and_process_knowledge_to_langchain_docs(knowledge_file_path, separator = "\n",chunk_size=64, chunk_overlap=0):
    documents = TextLoader(knowledge_file_path).load()
    text_splitter = CharacterTextSplitter(separator = separator,chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)

    return docs

def read_and_process_question_to_list(question_file_path, separator = "<sep>\n"):
    documents = TextLoader(question_file_path).load()
    question_list = []
    for document in documents:
        questions = document.page_content.split(separator)
        if questions != "":
            question_list.extend(questions)

    return question_list

def initial_langchain_embeddings(embeddings_model_name, model_kwargs, public):
    if public:
        os.environ["OPENAI_API_KEY"] = openai.api_key_path
        embedding_function = OpenAIEmbeddings()
    else:
        embedding_function = HuggingFaceEmbeddings(model_name=embeddings_model_name, model_kwargs=model_kwargs)

    return embedding_function 

def initial_or_read_langchain_database_faiss(documents, embedding_function, db_persist_directory, renew_vectordb=True):
    if not os.path.exists(db_persist_directory) or renew_vectordb:
        vectordb = FAISS.from_documents(documents=documents, embedding=embedding_function, consine_sim=True)
        vectordb.save_local(db_persist_directory)
        print("Successfully create and save database")
    else:
        vectordb = FAISS.load_local(db_persist_directory, embedding_function)

    return vectordb

