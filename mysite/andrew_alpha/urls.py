from django.urls import path
from andrew_alpha import views
from .views import process_image

urlpatterns = [
    path('', views.andrew_alpha, name='andrew_alpha'),
    path('process_image/', process_image),
]
