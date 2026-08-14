from django.urls import path
from . import views

urlpatterns = [
    # Les URLs sont gérées par django-ninja dans le fichier principal urls.py
    # Cette app utilise le router de ninja
]

# Le router est exporté pour être inclus dans le fichier principal
from .views import router