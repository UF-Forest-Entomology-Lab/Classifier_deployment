from django.urls import path
from andrew_alpha import views
from .views import upload_image

urlpatterns = [
    path('', views.andrew_alpha, name='andrew_alpha'),
    path('upload_image/', upload_image),
]
