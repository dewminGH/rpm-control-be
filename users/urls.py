from django.urls import path
from .views.login import  login
from .views.save_container_type import update_container_type

urlpatterns = [
    path('login/', login, name='login'),
    path('update_container_type/',update_container_type, name='update_container_type')
]