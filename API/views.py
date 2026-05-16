from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from django.db.models import Q
from API.serializers import (
    BookDetailSerializer,
    GenreSerializer,
    BookListSerializer,
    IssueOfBooksSerializer,
)
from engine.models import Book, IssueOfBooks, BookChapter, TocBook
from engine.models import Genre
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from fb2reader import fb2book
from djoser.serializers import UserSerializer
from django.db.models import F
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q

# Фикс для fb2reader
# class fb2_parser(fb2reader.fb2book):
#     def get_translators(self):
#         translators = []
#         for translator in self.soup.find_all("translator"):
#             first_name = translator.find("first-name").text
#             last_name = translator.find("last-name").text
#             if first_name != None:
#                 translatorsFL = first_name + " " + last_name
#                 translators.append(translatorsFL)
#         return translators


# Create your views here.
class TakeBook(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IssueOfBooksSerializer

    def perform_create(self, serializer):
        user = self.request.user
        book_id = self.kwargs["pk"]

        with transaction.atomic():
            updated = Book.objects.filter(id=book_id, web_amount__gt=0).update(
                web_amount=F("web_amount") - 1
            )

            if not updated:
                raise ValidationError({"error": "Книги закончились."})

            book = Book.objects.get(id=book_id)

            # проверка: уже взял эту книгу
            if IssueOfBooks.objects.filter(
                reader=user, book=book, return_date__isnull=True
            ).exists():
                raise ValidationError({"error": "Вы уже взяли эту книгу."})

            # проверка лимита
            user_issues = IssueOfBooks.objects.select_for_update().filter(
                reader=user, return_date__isnull=True
            )

            if user_issues.count() >= 5:
                raise ValidationError({"error": "Нельзя больше 5 книг."})

            serializer.save(reader=user, book=book, is_web=True)


class ReturnBook(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IssueOfBooksSerializer

    def get_queryset(self):
        return IssueOfBooks.objects.filter(reader=self.request.user)

    def perform_update(self, serializer):
        with transaction.atomic():
            issue = IssueOfBooks.objects.select_for_update().get(id=self.kwargs["pk"])
            book = issue.book

            if not issue.is_web:
                raise ValidationError(
                    {"error": "Только книги, взятые через веб, можно возвращать."}
                )

            if issue.return_date is not None:
                raise ValidationError({"error": "Книга уже была возвращена."})

            serializer.save(return_date=timezone.now().date())

            Book.objects.filter(id=book.id).update(web_amount=F("web_amount") + 1)

    def get_queryset(self):
        return IssueOfBooks.objects.filter(reader=self.request.user)


class BookDetailAPIView(generics.RetrieveAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()


class BookTOCAPIView(generics.RetrieveAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = TocBook.objects.all()

    lookup_field = "book_id"
    lookup_url_kwarg = "book_id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.toc)


class ChapterContentAPIView(generics.RetrieveAPIView):
    permission_classes = IsAuthenticated
    queryset = BookChapter.objects.all()

    def retrieve(self):
        instance = self.get_object()
        if not instance.file:
            return Response({"error": "Chapter file not found"}, status=404)
        try:
            with open(instance.file.path, "r", encoding="utf-8") as f:
                content = f.read()
            return HttpResponse(content, content_type="text/html; charset=utf-8")
        except IOError:
            return Response({"error": "Unable to read chapter file"}, status=500)


class Account(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class MyBooks(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IssueOfBooksSerializer
    pagination_class = None

    def get_queryset(self):
        return IssueOfBooks.objects.filter(reader=self.request.user).order_by(
            "return_date"
        )


class GenreListAPIView(generics.ListAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class BookListAPIView(generics.ListAPIView):
    serializer_class = BookListSerializer

    def get_queryset(self):
        query_str = self.request.GET.get("query")

        # Оптимизированная базовая выборка
        books = Book.objects.all().select_related("genre", "author", "publisher")

        if query_str:
            # Создаем вектор поиска по нужным полям.
            # 'russian' обеспечит поддержку склонений.
            vector = (
                SearchVector("title", weight="A")
                + SearchVector("author__first_name", weight="B")
                + SearchVector("author__last_name", weight="B")
                + SearchVector("genre__name", weight="C")
            )

            # SearchQuery также инициализируем с русским словарем
            search_query = SearchQuery(query_str, config="russian")

            # Фильтруем и ранжируем (сначала самые подходящие)
            books = (
                books.annotate(search=vector, rank=SearchRank(vector, search_query))
                .filter(search=search_query)
                .order_by("-rank")
            )

        return books


# region для поиска по названию и автору, фильтрация по жанру и году
# class BookListAPIView(generics.ListAPIView):
#     # permission_classes = (IsAuthenticated,)
#     serializer_class = BookListSerializer

#     def get_queryset(self):
#         query = self.request.GET.get("query")
#         genre = self.request.GET.get("genre")
#         year = self.request.GET.get("year")
#         author = self.request.GET.get("author")

#         books = Book.objects.all().select_related("genre", "author", "publisher")
#         if query:
#             books = books.filter(title__iregex=query)
#         if genre:
#             books = books.filter(genre_id=genre)
#         if year:
#             books = books.filter(year=year)
#         if author:
#             author_parts = author.split()
#             if len(author_parts) == 1:
#                 books = books.filter(
#                     Q(author__first_name__iregex=author_parts[0])
#                     | Q(author__last_name__iregex=author_parts[0])
#                 )
#             elif len(author_parts) >= 2:
#                 first_name, last_name = author_parts[:2]
#                 books = books.filter(
#                     Q(
#                         author__first_name__iregex=first_name,
#                         author__last_name__iregex=last_name,
#                     )
#                     | Q(
#                         author__first_name__iregex=last_name,
#                         author__last_name__iregex=first_name,
#                     )
#                 )
#         return books
# endregion


class TextAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        try:
            book_instance = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return Response({"error": "Книга не найдена"}, status=404)

        book = fb2book(book_instance.epub.path) if book_instance.epub else None

        body = (book.get_body() if book else None,)

        return HttpResponse(body)
