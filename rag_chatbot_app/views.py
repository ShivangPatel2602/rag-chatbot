from django.shortcuts import render

# Create your views here.
def rag_chatbot_app_view(req):
    return render(req, "rag_chatbot_app/index.html")