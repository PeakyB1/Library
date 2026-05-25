from django.urls import include, path, re_path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("v1/book/<int:pk>/", views.BookDetailAPIView.as_view()),
    path("v1/book/<int:book_id>/toc/", views.BookTOCAPIView.as_view()),
    path(
        "v1/book/<int:book_id>/chapter/<str:pointer>/",
        views.ChapterContentAPIView.as_view(),
    ),
    path(
        "v1/book/<int:book_id>/images/<str:image_name>/",
        views.BookImageAPIView.as_view(),
        name="protected-book-image",
    ),
    path("v1/book/list/", views.BookListAPIView.as_view()),
    path("v1/book/genres/", views.GenreListAPIView.as_view()),
    path("v1/book/text/<int:id>/", views.TextAPIView.as_view()),
    path("v1/drf-auth/", include("rest_framework.urls")),
    path("v1/account/", views.Account.as_view()),
    path("v1/book/take/<int:pk>/", views.TakeBook.as_view()),
    path("v1/account/return/<int:pk>/", views.ReturnBook.as_view()),
    path("v1/account/mybooks/", views.MyBooks.as_view()),
    # Эндпоинты Djoser для регистрации (/v1/auth/users/)
    path("v1/auth/", include("djoser.urls")),
    
    # Эндпоинты Djoser для JWT-токенов (/v1/auth/jwt/create/)
    path("v1/auth/", include("djoser.urls.jwt")),
]
