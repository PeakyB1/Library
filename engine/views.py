from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import BookFilterForm
from .models import Genre, Book, IssueOfBooks, Author
import datetime 
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
def returnBook(request, id):
    issue = IssueOfBooks.objects.get(id=id)
    book = issue.book
    if not issue.is_web:
        messages.error(request, "Только книги, взятые через веб, можно возвращать.")
        return redirect('account')
    issue.return_date = datetime.date.today()
    issue.save()
    book.web_amount += 1
    book.save()
    messages.success(request, "Книга успешно возвращена.")
    return redirect('account')
@login_required
def takeBook(request, id):
    is_web = request.GET.get('is_web')
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
    if is_web=='True' and book.web_amount <= 0:
        messages.error(request, "Нет доступных экземпляров книги.")
        return redirect('book_detail', id=id)
    if is_web=='False' and book.amount <= 0:
        messages.error(request, "Нет доступных экземпляров книги.")
        return redirect('book_detail', id=id)
    if is_web=='True':
        IssueOfBooks.objects.create(book=book, reader=user, issue_date=datetime.date.today(), is_web=is_web)
        book.web_amount -= 1
        book.save()
        messages.success(request, "Книга успешно взята.")
        return redirect('account')
    if is_web=='False':
        IssueOfBooks.objects.create(book=book, reader=user, issue_date=datetime.date.today(), is_web=is_web)
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
    paginate_by = 5 # 5 книг на страницу

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
        return context
    

