from django.urls import path
from . import views

app_name = 'crime'

urlpatterns = [
    path('', views.landing_page, name='landing'),
]
