import datetime
from django.contrib import admin
from .models import Author, Genre, Book, IssueOfBooks, Publisher
from django.db.models import F
# Register your models here.

class IssueOfBooksAdmin(admin.ModelAdmin):
    list_display = ('book', 'reader', 'issue_date', 'return_date')

    @admin.action(description="Отметить как возвращенные")
    def mark_as_returned(self, request, queryset):
        for issues in queryset:
            if not issues.return_date:
                issues.return_date = datetime.date.today()
                issues.book.amount = F('amount') + 1
                issues.save()
                issues.book.save()

    actions = [mark_as_returned]


admin.site.register(IssueOfBooks, IssueOfBooksAdmin)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Publisher)

