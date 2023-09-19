from django.urls import path
from andrew_alpha import views

urlpatterns = [
    path('', views.andrew_alpha, name='andrew_alpha'),
]