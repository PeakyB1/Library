from django.urls import include, path
from . import views

urlpatterns = [
    path('v1/book/<int:id>/', views.BookDetailAPIView.as_view()),
    path('v1/book/list/', views.BookListAPIView.as_view()),
    path('v1/book/genres/', views.GenreListAPIView.as_view()),
    path('v1/book/text/<int:id>/', views.TextAPIView.as_view()),
    path('v1/drf-auth/', include('rest_framework.urls')),
]