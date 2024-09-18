# estoque/urls.py
from django.urls import path
from .views import EstoqueListView, EstoqueCreateView

app_name = 'estoque'

urlpatterns = [
    path('', EstoqueListView.as_view(), name='estoque_list'),
    path('new/', EstoqueCreateView.as_view(), name='estoque_create'),
]

