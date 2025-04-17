# PROJECT WORKFLOW

This is a Retrieval Augmented Generation (RAG) based ChatBot application that is built on a Django Framework.

Below is a detailed documentation of how to setup the project and utilize the functionality:

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ShivangPatel2602/rag-chatbot.git
cd rag_chatbot
```

### 2. Set Up Virtual Environment
```python
python -m venv venv
source venv/bin/activate
```
You can also go ahead with using an existing python environment as well.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py migrate
```

#### 5. Start Server
```bash
python manage.py runserver
```

## General Workaround
1. All ChatBot interactions are handled via `rag_chatbot_app/chatbot.py`.
2. Frontend code resides in `rag_chatbot_app/templates/rag_chatbot_app/index.html`.
3. Frontend styling and additional styling resides in the `rag_chatbot_app/static/rag_chatbot_app/css/styles.css` and `rag_chatbot_app/static/rag_chatbot_app/js/chatbot.js`.
4. API initialization and calls are handled in the `config.py` file located in the root directory.

## Generating OpenAI API Key
To utilize the functionality of the chatbot, you'll need an OpenAI API key.

1. Go to [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
2. Log in and click `Create new secret key`
3. Copy the key and store it in a `.env` file in the root directory of the project
    ```env
    OPENAI_API_KEY=your-openai-api-key
    ```
4. To import the OpenAI API Key, use the `python-dotenv` library
    ```python
    import os
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ```