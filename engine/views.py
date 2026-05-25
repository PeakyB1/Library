from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import BookFilterForm
from .models import Genre, Book, IssueOfBooks, Author
from django.contrib.postgres.search import SearchVector
import datetime
from django.db import transaction


# Create your views here.
def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


@login_required
def account(request):
    user = request.user
    issued_books = IssueOfBooks.objects.filter(reader=user).order_by("return_date")
    books_count = issued_books.filter(return_date__isnull=True).count()
    context = {
        "issued_books": issued_books,
        "books_count": books_count,
    }
    return render(request, "account.html", context)


def book(request, id):
    book = Book.objects.get(id=id)
    context = {"book": book}
    return render(request, "book.html", context)


@login_required
def returnBook(request, id):
    try:
        issue = IssueOfBooks.objects.get(id=id)
    except IssueOfBooks.DoesNotExist:
        messages.error(request, "Запись не найдена.")
        return redirect("account")

    if not issue.is_web:
        messages.error(request, "Только книги, взятые через веб, можно возвращать.")
        return redirect("account")
    
    if issue.reader != request.user:
        messages.error(request, "Ошибка при возврате книги.")
        return redirect("account")
        
    if issue.return_date is not None:
        messages.error(request, "Книга уже была возвращена.")
        return redirect("account")

    with transaction.atomic():
        try:
            issue = IssueOfBooks.objects.select_for_update().get(id=id)
            book = Book.objects.select_for_update().get(id=issue.book_id)
        except (IssueOfBooks.DoesNotExist, Book.DoesNotExist):
            messages.error(request, "Ошибка при обновлении данных.")
            return redirect("account")

        issue.return_date = datetime.date.today()
        issue.save()
        
        book.web_amount += 1
        book.save()
    
    messages.success(request, "Книга успешно возвращена.")
    return redirect("account")


@login_required
def takeBook(request, id):
    is_web = request.GET.get("is_web") == "True"
    user = request.user

    with transaction.atomic():
        try:
            book = Book.objects.select_for_update().get(id=id)
        except Book.DoesNotExist:
            messages.error(request, "Книга не найдена.")
            return redirect("account")

        unreturned_books_count = IssueOfBooks.objects.filter(
            reader=user, return_date__isnull=True
        ).count()
        
        already_taken = IssueOfBooks.objects.filter(
            reader=user, return_date__isnull=True, book=book
        ).exists()

        if already_taken:
            messages.error(request, "Вы уже взяли эту книгу.")
            return redirect("book_detail", id=id)
            
        if unreturned_books_count >= 5:
            messages.error(request, "Вы не можете взять больше 5 книг.")
            return redirect("book_detail", id=id)

        if is_web:
            if book.web_amount <= 0:
                messages.error(request, "Нет доступных экземпляров книги.")
                return redirect("book_detail", id=id)
            book.web_amount -= 1
        else:
            if book.amount <= 0:
                messages.error(request, "Нет доступных экземпляров книги.")
                return redirect("book_detail", id=id)
            book.amount -= 1

        book.save()

        IssueOfBooks.objects.create(
            book=book, 
            reader=user, 
            issue_date=datetime.date.today(), 
            is_web=is_web
        )
    
    messages.success(request, "Книга успешно взята.")
    return redirect("account")





def contact(request):
    return render(request, "contact.html")


class SearchBooksView(ListView):
    model = Book
    template_name = "search.html"
    context_object_name = "books"
    paginate_by = 5 

    def get_queryset(self):
        """
        Метод для фильтрации книг на основе данных из формы.
        """
        books = Book.objects.all()
        self.form = BookFilterForm(self.request.GET or None, genres=Genre.objects.all())

        if self.form.is_valid():
            query = self.form.cleaned_data.get("query")
            genre_id = self.form.cleaned_data.get("genre")
            year = self.form.cleaned_data.get("year")
            author = self.form.cleaned_data.get("author")

            if query:
                books = books.filter(title__iregex=query)
            if genre_id:
                books = books.filter(genre_id=genre_id)
            if year:
                books = books.filter(year=year)
            if author:
                books = books.annotate(
                    # Создаем вектор поиска по двум полям
                    author_search=SearchVector('author__first_name', 'author__last_name')
                ).filter(
                    # Postgres сам разобьет `author` на слова и проверит их наличие в векторе
                    author_search=author
                )

        return books

    def get_context_data(self, **kwargs):
        """
        Добавление формы и жанров в контекст.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context
