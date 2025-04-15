import os
import sqlite3
import pickle
from numpy import dot
from numpy.linalg import norm
from config import client, OPENAI_API_KEY
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings 
from langchain_community.vectorstores import FAISS

DOCS_PATH = os.path.join(os.path.dirname(__file__), "docs")
DB_PATH = "query_memory.db"

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=OPENAI_API_KEY)

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

def load_documents():
    documents = []
    for filename in os.listdir(DOCS_PATH):
        path = os.path.join(DOCS_PATH, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(path)
        else:
            continue
        documents.extend(loader.load())
    return documents

def split_and_embed_documents():
    documents = load_documents()
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

vector_store = split_and_embed_documents()
retriever = vector_store.as_retriever()

def init_db():
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS query_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT NOT NULL,
                        response TEXT NOT NULL,
                        embedding BLOB NOT NULL
                    )
                    ''')
    connect.commit()
    connect.close()
    
init_db()

def store_query_response(query, response):
    query_embedding = embeddings.embed_query(query)
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute('''
                   INSERT INTO query_memory (query, response, embedding) 
                   VALUES (?, ?, ?)
                   ''', (query, response, pickle.dumps(query_embedding)))
    connect.commit()
    connect.close()
    
def get_similar_response(query):
    query_embedding = embeddings.embed_query(query)
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute("SELECT query, response, embedding FROM query_memory")
    rows = cursor.fetchall()
    connect.close()
    
    best_match = None
    best_similarity = 0.85
    
    for temp_query, temp_response, temp_embedding_blob in rows:
        temp_embedding = pickle.loads(temp_embedding_blob)
        similarity = cosine_similarity(query_embedding, temp_embedding)
        print(similarity)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = temp_response
            
    return best_match if best_match else None
    
    
def get_openai_response(prompt, query):
    store = get_similar_response(query)
    if store:
        return f"\n{store}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that provides answers to queries of students."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.9
        )
        
        if response and response.choices:
            final = response.choices[0].message.content.strip()
            store_query_response(query, final)
            return final
        return "Sorry, I couldn't generate a response. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"

def get_rag_response(query):
    relevant_docs = retriever.invoke(query)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = f"You are an experienced project manager with strong technical expertise. You are assisting a student in designing a project workflow.\nYour task is to provide **structured, high-level outlines** that help the student break down the project into manageable steps.\nYou should **never provide the entire project solution**—if asked, politely decline and redirect the student toward conceptual guidance.\nYour responses should be **concise, precise, and easy to follow**, offering practical steps while maintaining a friendly, human-like tone.\nConsider the context provided carefully before responding.\n\nContext: {context}\n\nQuery:{query}"
    
    raw_response = get_openai_response(prompt, query)
    return raw_response
