from django.urls import path
from .views import rag_chatbot_app_view

urlpatterns = [
    path('', rag_chatbot_app_view, name="rag_chatbot_app")
]