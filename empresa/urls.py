# empresa/urls.py
from django.urls import path
from .views import EmpresaListView, EmpresaDetailView

app_name = 'empresa'

urlpatterns = [
    path('', EmpresaListView.as_view(), name='empresa_list'),
    path('<int:pk>/', EmpresaDetailView.as_view(), name='empresa_detail'),
]

