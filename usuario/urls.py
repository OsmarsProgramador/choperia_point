# usuario/urls.py
from django.urls import path
from .views import UserLoginView, UserLogoutView, UserSignupView

app_name = 'usuario'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('signup/', UserSignupView.as_view(), name='signup'),
]

