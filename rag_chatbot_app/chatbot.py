import os
from config import client
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

def get_openai_response(query):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that provides answers to queries of students."},
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=0.9
        )
        
        if response and response.choices:
            return response.choices[0].message.content.strip()
        return "Sorry, I couldn't generate a response. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"

def get_rag_response(query):
    relevant_docs = retriever.invoke(query)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = f"You are a project manager who has commendable technical expertise. You are helping a student to create a project workflow. You can only give outline for it and not the entire solution. If someone asks for creating the entire project just tell them you cannot do that. Your response should be more like a human response and not something generated from a bot. You should stick to the solution provided to you and nothing else. Your response should be precise and easy to understand.\n\nBased on the following context, answer the question:\n\nContext: {context}\n\nQuestion: {query}"
    
    raw_response = get_openai_response(prompt)
    return raw_response


    