from django.urls import path
from . import views

urlpatterns = [
    path('', views.rag_chatbot_app_view, name="rag_chatbot_app"),
    path('ask_chatbot/', views.ask_chatbot, name='ask_chatbot')
]