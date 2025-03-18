from django.shortcuts import render
from django.http import JsonResponse
import json

def get_chatbot_response(user_input):
    user_input = user_input.lower()
    responses = {
        "hi": "Hello! How can I help you?",
        "what do you do?": "I am a chatbot designed to assist you with LLM-related tasks and answer your queries.",
        "bye": "Goodbye! Have a great day!"
    }  
    
    return responses.get(user_input, "Sorry, I don't understand that. Can you rephrase?")  
    
def rag_chatbot_app_view(req):
    return render(req, "rag_chatbot_app/index.html")

def ask_chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        chatbot_response = get_chatbot_response(user_msg)
        return JsonResponse({"response": chatbot_response})
    return JsonResponse({"response": "Invalid request!"})