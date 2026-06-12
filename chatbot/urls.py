from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('message/',     views.chat_message,     name='message'),
    path('history/',     views.chat_history,      name='history'),
    path('suggestions/', views.chat_suggestions,  name='suggestions'),
    path('clear/',       views.chat_clear,        name='clear'),
]
