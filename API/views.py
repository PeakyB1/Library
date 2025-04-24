import datetime
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from django.db.models import Q
from API.serializers import (
    BookDetailSerializer,
    GenreSerializer,
    BookListSerializer,
    IssueOfBooksSerializer,
)
from engine.models import Book, IssueOfBooks
from engine.models import Genre
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
import fb2reader
from djoser.serializers import UserSerializer


# Фикс для fb2reader
class fb2_parser(fb2reader.fb2book):
    def get_translators(self):
        translators = []
        for translator in self.soup.find_all("translator"):
            first_name = translator.find("first-name").text
            last_name = translator.find("last-name").text
            if first_name != None:
                translatorsFL = first_name + " " + last_name
                translators.append(translatorsFL)
        return translators


# Create your views here.
class TakeBook(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IssueOfBooksSerializer

    def perform_create(self, serializer):
        user = self.request.user
        book = Book.objects.get(id=self.kwargs["pk"])
        unreturned_books_count = IssueOfBooks.objects.filter(
            reader=user, return_date__isnull=True
        ).count()

        if IssueOfBooks.objects.filter(
            reader=user, book=book, return_date__isnull=True
        ).exists():
            raise ValidationError({"error": "Вы уже взяли эту книгу."})

        if unreturned_books_count >= 5:
            raise ValidationError(
                {"error": "Вы не можете взять больше 5 книг одновременно."}
            )
        if book.web_amount <= 0:
            raise ValidationError({"error": "Нет доступных экземпляров этой книги."})
        serializer.save(reader=user, book=book, is_web=True)


class ReturnBook(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IssueOfBooksSerializer

    def perform_update(self, serializer):
        user = self.request.user
        issue = IssueOfBooks.objects.get(id=self.kwargs["pk"])
        book = issue.book

        if not issue.is_web:
            raise ValidationError(
                {"error": "Только книги, взятые через веб, можно возвращать."}
            )
        if issue.return_date is not None:
            raise ValidationError({"error": "Книга уже была возвращена."})

        serializer.save(return_date=datetime.date.today())
        book.web_amount += 1
        book.save()
        return Response({"success": "Книга успешно возвращена."})

    def get_queryset(self):
        return IssueOfBooks.objects.filter(reader=self.request.user)


class BookDetailAPIView(generics.RetrieveAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()


class Account(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class MyBooks(generics.ListAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = IssueOfBooksSerializer

    def get_queryset(self):
        return IssueOfBooks.objects.filter(reader=self.request.user).order_by(
            "return_date"
        )


class GenreListAPIView(generics.ListAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class BookListAPIView(generics.ListAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = BookListSerializer

    def get_queryset(self):
        query = self.request.GET.get("query")
        genre = self.request.GET.get("genre")
        year = self.request.GET.get("year")
        author = self.request.GET.get("author")

        books = Book.objects.all().select_related("genre", "author", "publisher")
        if query:
            books = books.filter(title__iregex=query)
        if genre:
            books = books.filter(genre_id=genre)
        if year:
            books = books.filter(year=year)
        if author:
            author_parts = author.split()
            if len(author_parts) == 1:
                books = books.filter(
                    Q(author__first_name__iregex=author_parts[0])
                    | Q(author__last_name__iregex=author_parts[0])
                )
            elif len(author_parts) >= 2:
                first_name, last_name = author_parts[:2]
                books = books.filter(
                    Q(
                        author__first_name__iregex=first_name,
                        author__last_name__iregex=last_name,
                    )
                    | Q(
                        author__first_name__iregex=last_name,
                        author__last_name__iregex=first_name,
                    )
                )
        return books


class TextAPIView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        try:
            book_instance = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return Response({"error": "Книга не найдена"}, status=404)

        book = fb2_parser(book_instance.fb2file.path) if book_instance.fb2file else None

        body = (book.get_body() if book else None,)

        return HttpResponse(body)
