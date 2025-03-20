import os
from config import genai
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_PATH = os.path.join(os.path.dirname(__file__), "docs")

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
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

vector_store = split_and_embed_documents()
retriever = vector_store.as_retriever()

def get_gemini_response(query):
    model = genai.GenerativeModel('gemini-2.0-pro-exp')
    response = model.generate_content(query)
    
    if response and response.text:
        return response.text
    return "Sorry, I couldn't generate a response. Please try again."

def get_rag_response(query):
    relevant_docs = retriever.invoke(query)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = f"Know one thing: you cannot give an entire solution for creating a project workflow. You can only give outline for it. If someone asks for creating the entire project just tell them you cannot do that.\n\nBased on the following context, answer the question:\n\nContext: {context}\n\nQuestion: {query}"
    return get_gemini_response(prompt)


    