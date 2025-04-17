from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='user_login'),
    path('register/', views.RegisterUser.as_view(), name='user_register'),
    path('logout/', LogoutView.as_view(), name='user_logout'),
]
