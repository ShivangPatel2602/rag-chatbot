import os
import sqlite3
import pickle
import json
import re
from numpy import dot
from numpy.linalg import norm
from config import client, OPENAI_API_KEY, MONGODB_CONFIG, ENV
from datetime import datetime
import nltk
from pymongo import MongoClient
from bson.binary import Binary
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import OpenAIEmbeddings 
from langchain_community.vectorstores import FAISS

class QueryProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.query_types = {
            'explanation': r'(explain|describe|what|how).+(mean|is|are|works?)',
            'comparison': r'(compare|difference|versus|vs)',
            'example': r'(example|sample|show)',
            'implementation': r'(implement|code|create|build|make)',
            'troubleshooting': r'(error|issue|problem|fix|debug|wrong)'
        }
        
    def process_query(self, query: str) -> dict:
        clean_query = re.sub(r'[^\w\s]', '', query.lower())
        tokens = word_tokenize(clean_query)
        key_terms = [w for w in tokens if w not in self.stop_words]
        
        return {
            'clean_query': clean_query,
            'query_type': self._classify_query(query),
            'key_terms': key_terms,
            'sentiment': TextBlob(query).sentiment.polarity,
            'complexity': len(tokens) 
        }
    
    def _classify_query(self, query: str) -> str:
        for qtype, pattern in self.query_types.items():
            if re.search(pattern, query, re.IGNORECASE):
                return qtype
        return 'general'
    
class ResponseManager:
    def __init__(self):
        self.temperature_map = {
            'explanation': 0.3,
            'comparison': 0.4,
            'example': 0.7,
            'implementation': 0.2,
            'troubleshooting': 0.3,
            'general': 0.5
        }
        self.token_map = {
            'explanation': 400,
            'comparison': 500,
            'example': 300,
            'implementation': 600,
            'troubleshooting': 400,
            'general': 500
        }
        
    def get_parameters(self, query_metadata: dict) -> dict:
        query_type = query_metadata['query_type']
        complexity = query_metadata['complexity']
        
        base_temp = self.temperature_map.get(query_type, 0.5)
        base_tokens = self.token_map.get(query_type, 500)
        adjusted_tokens = min(1000, base_tokens * (1 + (complexity / 100)))
        
        return {
            'temperature': base_temp,
            'max_tokens': int(adjusted_tokens),
            'presence_penalty': 0.6,
            'frequency_penalty': 0.3
        }
        
class DatabaseManager:
    def __init__(self):
        self.config = MONGODB_CONFIG[ENV]
        if ENV == 'dev':
            self.client = MongoClient(
                host=self.config['host'],
                port=self.config['port']
            )
        else:
            self.client = MongoClient(self.config['uri'])
            
        self.db = self.client[self.config['db_name']]
        self.collection = self.db[self.config['collection_name']]
        
        self.collection.create_index([('query', 'text')])
        self.collection.create_index([('timestamp', -1)])

    def store_query_response(self, query, response, metadata=None):
        query_embedding = embeddings.embed_query(query)
        document = {
            'query': query,
            'response': response,
            'embedding': Binary(pickle.dumps(query_embedding)),
            'metadata': metadata,
            'timestamp': datetime.now()
        }
        self.collection.insert_one(document)

    def get_similar_response(self, query):
        query_embedding = embeddings.embed_query(query)
        best_match = None
        best_similarity = 0.85

        cursor = self.collection.find({}, {'response': 1, 'embedding': 1})
        
        for doc in cursor:
            temp_embedding = pickle.loads(doc['embedding'])
            similarity = cosine_similarity(query_embedding, temp_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = doc['response']
                
        return best_match if best_match else None

    def get_recent_queries(self, limit=10):
        return list(self.collection.find(
            {},
            {'query': 1, 'response': 1, 'metadata': 1, 'timestamp': 1, '_id': 0}
        ).sort('timestamp', -1).limit(limit))
    
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
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " "]
    )
    chunks = text_splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata.update({
            "chunk_id": i,
            "source": "project_docs",
            "timestamp": datetime.now().isoformat()
        })
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

vector_store = split_and_embed_documents()
retriever = vector_store.as_retriever()
db_manager = DatabaseManager()
    
def get_openai_response(prompt, query, store_response=False):
    store = db_manager.get_similar_response(query)
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
            if store_response:
                db_manager.store_query_response(query, final)
            return final
        return "Sorry, I couldn't generate a response. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"

def get_rag_response(query: str) -> str:
    query_processor = QueryProcessor()
    response_manager = ResponseManager()
    
    query_metadata = query_processor.process_query(query)
    
    relevant_docs = retriever.invoke(query_metadata['clean_query'])
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = f"""You are an experienced project manager with strong technical expertise.
    
    Instructions:
    1. Provide structured, high-level guidance
    2. Break down complex concepts into manageable steps
    3. Focus on conceptual understanding
    4. Maintain educational value without providing complete solutions
    5. Be concise and precise
    6. Use bullet points for clarity
    
    Remember that your responses are targeted for students and should be educational in nature. Responses should maintain academic integrity and not provide complete solutions to assignments or projects.

    Query: {query_metadata['clean_query']}
    Context Information:
    {context}
    """
    
    raw_response = get_openai_response(prompt, query, store_response=False)
    db_manager.store_query_response(query, raw_response, {
        **query_metadata,
        'timestamp': datetime.now().isoformat(),
        'model': 'gpt-3.5-turbo'
    })
    return raw_response