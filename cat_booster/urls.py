from django.urls import path
from .views.cat_preds_view import cat_preds_fbv
from .views.base import home

urlpatterns = [
    path('', home, name='home'),
    path('predict/', cat_preds_fbv, name='cat-predict'),
]
