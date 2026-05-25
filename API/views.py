import os

from rest_framework.exceptions import ValidationError
from django.http import FileResponse, Http404, HttpResponse
from django.db.models import Q, F
from API.serializers import (
    BookDetailSerializer,
    GenreSerializer,
    BookListSerializer,
    IssueOfBooksSerializer,
)
from engine.models import Book, IssueOfBooks, BookChapter, TocBook, Genre
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from djoser.serializers import UserSerializer
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank


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

            if IssueOfBooks.objects.filter(
                reader=user, book=book, return_date__isnull=True
            ).exists():
                raise ValidationError({"error": "Вы уже взяли эту книгу."})

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


class BookDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BookDetailSerializer
    queryset = Book.objects.all()


class BookTOCAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TocBook.objects.all()

    lookup_field = "book_id"
    lookup_url_kwarg = "book_id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.toc)


class ChapterContentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, book_id, pointer):
        # 1. Считаем общее количество глав в книге для логики кнопок "Вперед/Назад"
        total_chapters = BookChapter.objects.filter(book_id=book_id).count()

        # 2. Определяем, как искать главу (по номеру или по имени файла)
        try:
            if pointer.isdigit():
                # Если передали число (например, "3"), ищем по порядковому номеру
                chapter = BookChapter.objects.get(book_id=book_id, number=int(pointer))
            else:
                # Если передали строку (например, "ch1-5.xhtml"), ищем по концу пути файла
                chapter = BookChapter.objects.get(
                    book_id=book_id, title = pointer
                )
        except BookChapter.DoesNotExist:
            return Response({"error": "Глава не найдена"}, status=404)

        # 3. Проверяем файл на диске и читаем его контент
        if not chapter.file or not os.path.exists(chapter.file.path):
            return Response({"error": "Файл главы отсутствует на сервере"}, status=404)

        try:
            with open(chapter.file.path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except IOError:
            return Response({"error": "Не удалось прочитать файл главы"}, status=500)

        # 4. Возвращаем стандартный DRF Response. Он сам превратит всё в JSON
        return Response(
            {
                "id": chapter.id,
                "number": chapter.number,
                "title": chapter.title,  # Там теперь лежит чистое имя файла благодаря фиксу в сервисе
                "content": html_content,
                "total_chapters": total_chapters,
            }
        )

class BookImageAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, book_id, image_name):
        # 1. Проверяем доступ пользователя к книге через запрос к базе
        # НАПРИМЕР: проверяем, есть ли запись, что этот юзер взял эту книгу и еще не вернул
        # has_access = TakeBook.objects.filter(user=request.user, book_id=book_id).exists()
        
        # ВРЕМЕННО для теста: заглушка (пропускает любого авторизованного юзера)
        has_access = True 

        if not has_access:
            return Response({"error": "Нет доступа к книге"}, status=403)

        # 2. Строим путь к картинке
        file_path = settings.PRIVATE_MEDIA_ROOT / 'books' / str(book_id) / 'images' / image_name

        if not file_path.exists():
            raise Http404("Изображение не найдено")

        # 3. Отдаем файл
        response = FileResponse(file_path.open('rb'))
        return response


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
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class BookListAPIView(generics.ListAPIView):
    serializer_class = BookListSerializer

    def get_queryset(self):
        query_str = self.request.GET.get("query")
        books = Book.objects.all().select_related("genre", "author", "publisher")

        if query_str:
            vector = (
                SearchVector("title", weight="A")
                + SearchVector("author__first_name", weight="B")
                + SearchVector("author__last_name", weight="B")
                + SearchVector("genre__name", weight="C")
            )

            search_query = SearchQuery(query_str, config="russian")
            books = (
                books.annotate(search=vector, rank=SearchRank(vector, search_query))
                .filter(search=search_query)
                .order_by("-rank")
            )

        return books

