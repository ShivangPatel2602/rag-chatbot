import os

MONGODB_CONFIG = {
    'dev': {
        'host': 'localhost',
        'port': 27017,
        'db_name': 'rag_chatbot',
        'collection_name': 'query_memory'
    }
}

ENV = os.environ.get('ENVIRONMENT', 'dev')