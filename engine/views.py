from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import BookFilterForm
from .models import Genre, Book, IssueOfBooks, Author
import datetime 
from rest_framework.views import APIView
from rest_framework.response import Response
import fb2reader
# Create your views here.
def index(request):
    return render(request, "index.html")
def about(request):
    return render(request, "about.html")
@login_required
def account(request):
    user = request.user
    issued_books = IssueOfBooks.objects.filter(reader=user).order_by('return_date')
    context = {
        'issued_books': issued_books,
    }
    return render(request, "account.html", context)

def book(request, id):
    book = Book.objects.get(id = id)
    context = {'book': book}
    return render(request, "book.html", context)
@login_required
def takeBook(request, id):
    book = Book.objects.get(id=id)
    user = request.user
    unreturned_books_count = IssueOfBooks.objects.filter(reader=user, return_date__isnull=True).count()
    unreturned_books = IssueOfBooks.objects.filter(reader=user, return_date__isnull=True, book=book)
    if unreturned_books:
        messages.error(request, "Вы уже взяли эту книгу.")
        return redirect('book_detail', id=id)
    if unreturned_books_count >= 5:
        messages.error(request, "Вы не можете взять больше 5 книг.")
        return redirect('book_detail', id=id)
    
    if book.amount <= 0:
        messages.error(request, "Нет доступных экземпляров книги.")
        return redirect('book_detail', id=id)
    
    IssueOfBooks.objects.create(book=book, reader=user, issue_date=datetime.date.today())
    book.amount -= 1
    book.save()
    messages.success(request, "Книга успешно взята.")
    return redirect('account')
def contact(request):
    return render(request, "contact.html")
class SearchBooksView(ListView):
    model = Book
    template_name = 'search.html'
    context_object_name = 'books'
    paginate_by = 5  # 5 книг на страницу

    def get_queryset(self):
        """
        Метод для фильтрации книг на основе данных из формы.
        """
        books = Book.objects.all()
        self.form = BookFilterForm(self.request.GET or None, genres=Genre.objects.all())
        
        if self.form.is_valid():
            query = self.form.cleaned_data.get('query')
            genre_id = self.form.cleaned_data.get('genre')
            year = self.form.cleaned_data.get('year')
            author = self.form.cleaned_data.get('author')

            if query:
                books = books.filter(title__iregex=query)
            if genre_id:
                books = books.filter(genre_id=genre_id)
            if year:
                books = books.filter(year=year)
            if author:
            # Разделяем строку по пробелам
                author_parts = author.split()
                if len(author_parts) == 1:
                    # Если введена только одна часть (имя или фамилия)
                    books = books.filter(Q(author__first_name__iregex=author_parts[0]) | Q(author__last_name__iregex=author_parts[0]))
                elif len(author_parts) >= 2:
                    # Если введены обе части (имя и фамилия)
                    first_name = author_parts[0]
                    last_name = author_parts[1]
                    books = books.filter(Q(author__first_name__iregex=first_name, author__last_name__iregex=last_name) |
                                        Q(author__first_name__iregex=last_name, author__last_name__iregex=first_name))
        return books

    def get_context_data(self, **kwargs):
        """
        Добавление формы и жанров в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['page_range'] = context['paginator'].get_elided_page_range(number=context['page_obj'].number)
        context['current_page'] = context['page_obj'].number
        context['total_pages'] = context['paginator'].num_pages
        return context
    

class EngineAPIView(APIView):
    def get(self, request, id):
        file = Book.objects.get(id=id).fb2file
        book = fb2reader.fb2book(file.path)
        title = book.get_title()
        identifier = book.get_identifier()
        authors = Book.objects.get(id=id).author.first_name + " " + Book.objects.get(id=id).author.last_name
        translators = book.get_translators()
        series = book.get_series()
        lang = book.get_lang()
        description = book.get_description()
        # tags = book.get_tags()
        isbn = book.get_isbn()
        cover_image = Book.objects.get(id=id).cover_url.replace('\\', '/')
        return Response({
            'Название': title,
            'Идентификатор': identifier,
            'Авторы': authors,
            'Переводчики': translators,
            'Серия': series,
            'Язык': lang,
            'Описание': description,
            # 'Теги': tags,
            'ISBN': isbn,
            'Обложка': cover_image
        })