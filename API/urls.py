from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path('v1/book/<int:pk>/', views.BookDetailAPIView.as_view()),
    path('v1/book/list/', views.BookListAPIView.as_view()),
    path('v1/book/genres/', views.GenreListAPIView.as_view()),
    path('v1/book/text/<int:id>/', views.TextAPIView.as_view()),
    path('v1/drf-auth/', include('rest_framework.urls')),
    path('v1/account/', views.Account.as_view()),
    path('v1/auth/', include('djoser.urls')),
    path('v1/book/take/<int:pk>/', views.TakeBook.as_view()),
    path('v1/account/return/<int:pk>/', views.ReturnBook.as_view()),
    path('v1/account/mybooks/', views.MyBooks.as_view()),
    re_path(r'^v1/auth/', include('djoser.urls.authtoken')),
]