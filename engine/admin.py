from django.utils import timezone
from django.contrib import admin
from django.db.models import F
from .models import Author, Genre, Book, IssueOfBooks, Publisher
from .services import EpubImportService
from django.db import transaction

# Register your models here.


class IssueOfBooksAdmin(admin.ModelAdmin):
    list_display = ("book", "reader", "issue_date", "return_date", "is_web")

    @admin.action(description="Отметить как возвращенные")
    @transaction.atomic
    def mark_as_returned(self, request, queryset):
        for issue in queryset:
            if not issue.return_date:
                issue.return_date = timezone.now()
                issue.save(update_fields=["return_date"])
                if issue.is_web:
                    issue.book.web_amount = F("web_amount") + 1
                    issue.book.save(update_fields=["web_amount"])
                else:
                    issue.book.amount = F("amount") + 1
                    issue.book.save(update_fields=["amount"])

    actions = [mark_as_returned]


class BookAdmin(admin.ModelAdmin):
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        previous_file = None
        if change and obj.pk:
            previous_file = Book.objects.get(pk=obj.pk).epub
        super().save_model(request, obj, form, change)
        if obj.epub and obj.epub.name.lower().endswith(".epub"):
            epub_changed = not change or obj.epub.name != getattr(
                previous_file, "name", None
            )
            if epub_changed:
                EpubImportService(obj).parse_and_save(obj.epub.path)


admin.site.register(Book, BookAdmin)
admin.site.register(IssueOfBooks, IssueOfBooksAdmin)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Publisher)
