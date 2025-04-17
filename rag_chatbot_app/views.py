import json
from django.shortcuts import render
from django.http import JsonResponse
from .chatbot import get_rag_response
import speech_recognition as sr

def get_chatbot_response(user_input):
    user_input = user_input.lower()
    responses = {
        "hi": "Hello! How can I help you?",
        "what do you do?": "I am a chatbot designed to assist you with LLM-related tasks and answer your queries.",
        "bye": "Goodbye! Have a great day!"
    }  
    
    if user_input in responses:
        return responses[user_input]
    
    return get_rag_response(user_input)
    
def rag_chatbot_app_view(req):
    return render(req, "rag_chatbot_app/index.html")

def ask_chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        chatbot_response = get_chatbot_response(user_msg)
        return JsonResponse({"response": chatbot_response})
    return JsonResponse({"response": "Invalid request!"})

def transcribe_audio(request):
    print("entered transcribe audio")
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        print("Audio file received", audio_file)
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                transcription = recognizer.recognize_google(audio_data)
                print("Transcription", transcription)
                return JsonResponse({"transcription": transcription})
        except Exception as e:
            return JsonResponse({"transcription": '', "error": str(e)})
    return JsonResponse({"transcription": '', "error": "Invalid request!"})
