from django.urls import path
from .views.cat_preds_view import cat_preds_fbv
from .views.test import home

urlpatterns = [
    path('predict/', cat_preds_fbv, name='cat-predict'),
    path('', home,'home')
]
