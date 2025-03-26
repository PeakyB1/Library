from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from engine.models import Book
from rest_framework.views import APIView
from rest_framework.response import Response
import fb2reader
class fb2_parser(fb2reader.fb2book):
    def get_translators(self):
        translators = []
        for translator in self.soup.find_all('translator'):
            first_name = translator.find('first-name').text
            last_name = translator.find('last-name').text
            if first_name != None:
                translatorsFL = first_name + " " + last_name    
                translators.append(translatorsFL)
        return translators
# Create your views here.
class BookListAPIView(APIView):
    def get(self, request):
        query = request.GET.get('query')
        genre = request.GET.get('genre')
        year = request.GET.get('year')
        author = request.GET.get('author')

        books = Book.objects.all().select_related('genre', 'author', 'publisher') 

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
                    Q(author__first_name__iregex=author_parts[0]) | 
                    Q(author__last_name__iregex=author_parts[0])
                )
            elif len(author_parts) >= 2:
                first_name, last_name = author_parts[:2]
                books = books.filter(
                    Q(author__first_name__iregex=first_name, author__last_name__iregex=last_name) |
                    Q(author__first_name__iregex=last_name, author__last_name__iregex=first_name)
                )

        # Формируем список книг вручную, без использования values()
        books_list = []
        for book in books:
            books_list.append({
                "id": book.id,
                "title": book.title,
                "author": f"{book.author.first_name} {book.author.last_name}",
                "year": book.year,
                "genre": book.genre.name,
                "publisher": book.publisher.name,
                "file": "Есть электронная версия" if book.fb2file else "Нет электронной версии"
            })

        return Response(books_list)


class BookDetailAPIView(APIView):
    def get(self, request, id):
        try:
            book_instance = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return Response({"error": "Книга не найдена"}, status=404)
        
        book = fb2_parser(book_instance.fb2file.path) if book_instance.fb2file else None
        
        response_data = {
            'Название': book_instance.title if book_instance.title else None,
            'Год': book_instance.year if book_instance.year else None,
            'Идентификатор': book.get_identifier() if book else None,
            'Авторы': f"{book_instance.author.first_name} {book_instance.author.last_name}" if book_instance.author else None,
            'Переводчики': book.get_translators() if book else None,
            'Серия': book.get_series() if book else None,
            'Язык': book.get_lang() if book else None,
            'Описание': book_instance.summary if book_instance.summary else None,
            'Жанр': book_instance.genre.name if book_instance.genre else None,
            'ISBN': book.get_isbn() if book else None,
            'Обложка': book_instance.cover_url.replace('\\', '/') if book_instance.cover_url else None,
            'file': "Есть электронная версия" if book_instance.fb2file else "Файл не загружен",
        }
        
        return Response(response_data)