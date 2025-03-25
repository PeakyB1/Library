from django.db import models
from django.contrib.auth import get_user_model

class Author(models.Model):
    first_name = models.CharField(max_length=30, verbose_name="Имя")  # Имя автора
    last_name = models.CharField(max_length=30, verbose_name="Фамилия")  # Фамилия автора

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"  # Отображение имени и фамилии автора


class Genre(models.Model):
    name = models.CharField(max_length=20, verbose_name="Жанр")  # Название жанра

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name  # Отображение названия жанра


class Publisher(models.Model):
    name = models.CharField(max_length=30, verbose_name="Издатель")  # Название издателя

    class Meta:
        verbose_name = "Издатель"
        verbose_name_plural = "Издатели"

    def __str__(self):
        return self.name  # Отображение названия издателя


class Book(models.Model):
    title = models.CharField(max_length=30, verbose_name="Название книги")  # Название книги
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="Автор")  # Связь с автором
    year = models.IntegerField(verbose_name="Год издания")  # Год издания книги
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="Жанр")  # Связь с жанром книги
    amount = models.IntegerField(verbose_name="Количество экземпляров")  # Количество экземпляров
    web_amount = models.IntegerField(default=0, verbose_name="Количество экземпляров в интернет-библиотеке")
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, verbose_name="Издатель")  # Связь с издателем
    fb2file = models.FileField(upload_to='books/', max_length=100, null=True, verbose_name="Файл книги")
    summary = models.TextField(
        max_length=1000,
        help_text="Введите краткое описание книги",
        verbose_name="Аннотация книги",
    )  # Аннотация книги
    cover_url = models.URLField(blank=True, null=True)
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.title  # Отображение названия книги


class IssueOfBooks(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")  # Связь с книгой
    reader = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts',null=True, default=None)
    issue_date = models.DateField(verbose_name="Дата выдачи")  # Дата выдачи книги
    return_date = models.DateField(null=True, blank=True, verbose_name="Дата возврата")  # Дата возврата книги
    is_web = models.BooleanField(verbose_name="Веб-версия", default=False)  # Флаг для веб-версии книги
    class Meta:
        verbose_name = "Выдача книги"
        verbose_name_plural = "Выдачи книг"

    def __str__(self):
        return f"Выдача {self.id} - {self.book.title}. Читатель: {self.reader.first_name}"  # Отображение информации о выдаче
    
    