import os

MONGODB_CONFIG = {
    'dev': {
        'host': 'localhost',
        'port': 27017,
        'db_name': 'rag_chatbot',
        'collection_name': 'query_memory'
    },
    'prod': {
        'uri': os.environ.get('MONGODB_URI', ''),
        'db_name': os.environ.get('DB_NAME', 'rag_chatbot'),
        'collection_name': 'query_memory'
    }
}

ENV = os.environ.get('ENV', 'dev')