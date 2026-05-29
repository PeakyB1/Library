from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.storage import FileSystemStorage

private_media_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)


def chapter_upload_path(instance, filename):
    return f"books/{instance.book.id}/chapters/{filename}"


class Author(models.Model):
    first_name = models.CharField(max_length=30, verbose_name="Имя")
    last_name = models.CharField(max_length=30, verbose_name="Фамилия")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=30, verbose_name="Жанр")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=30, verbose_name="Издатель")

    class Meta:
        verbose_name = "Издатель"
        verbose_name_plural = "Издатели"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название книги")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="Автор")
    year = models.IntegerField(verbose_name="Год издания")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="Жанр")
    amount = models.IntegerField(verbose_name="Количество экземпляров")
    web_amount = models.IntegerField(
        default=0, verbose_name="Количество экземпляров в интернет-библиотеке"
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, verbose_name="Издатель"
    )
    epub = models.FileField(
        upload_to="books/",
        storage=private_media_storage,
        max_length=100,
        blank=True,
        verbose_name="Файл книги",
    )
    summary = models.TextField(
        max_length=1000,
        help_text="Введите краткое описание книги",
        verbose_name="Аннотация книги",
    )
    cover = models.ImageField(
        upload_to="covers/",
        verbose_name="Обложка",
        default="covers/default_cover.png",
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.title


class TocBook(models.Model):
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        verbose_name="Книга",
    )

    toc = models.JSONField(default=list)

    class Meta:
        verbose_name = "Оглавление книги"
        verbose_name_plural = "Оглавления книг"

    def __str__(self):
        return f"{self.book.title} - Оглавление"


class IssueOfBooks(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    reader = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name="posts",
        null=True,
        default=None,
    )
    issue_date = models.DateField(verbose_name="Дата выдачи", auto_now_add=True)
    return_date = models.DateField(null=True, blank=True, verbose_name="Дата возврата")
    is_web = models.BooleanField(verbose_name="Веб-версия")

    class Meta:
        verbose_name = "Выдача книги"
        verbose_name_plural = "Выдачи книг"

    def __str__(self):
        return (
            f"Выдача {self.id} - {self.book.title}. Читатель: {self.reader.first_name}"
        )


class BookChapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга")
    title = models.CharField(max_length=100, verbose_name="Название главы")
    number = models.IntegerField(verbose_name="Номер главы")

    file = models.FileField(
        storage=private_media_storage,
        upload_to=chapter_upload_path,
        max_length=255,
        blank=True,
        verbose_name="Файл главы",
    )

    class Meta:
        verbose_name = "Глава книги"
        verbose_name_plural = "Главы книг"

    def __str__(self):
        return f"{self.book.title} - {self.title}"
