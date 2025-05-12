import environ
from openai import OpenAI

env = environ.Env()
environ.Env.read_env()

OPENAI_API_KEY = env("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

MONGODB_CONFIG = {
    'dev': {
        'host': 'localhost',
        'port': 27017,
        'db_name': 'rag_chatbot',
        'collection_name': 'query_memory'
    },
    'prod': {
        'uri': env('MONGODB_URI'),
        'db_name': env('DB_NAME', default='rag_chatbot'),
        'collection_name': 'query_memory'
    }
}
ENV = env("ENV", default='dev')