from django.urls import path
from . import views

urlpatterns = [
    path('v1/book/<int:id>/', views.BookDetailAPIView.as_view()),
    path('v1/book/list/', views.BookListAPIView.as_view()),
]