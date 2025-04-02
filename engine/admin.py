import datetime
from django.contrib import admin
from .models import Author, Genre, Book, IssueOfBooks, Publisher
from django.db.models import F
# Register your models here.

class IssueOfBooksAdmin(admin.ModelAdmin):
    list_display = ('book', 'reader', 'issue_date', 'return_date', 'is_web')

    @admin.action(description="Отметить как возвращенные")
    def mark_as_returned(self, request, queryset):
        for issue in queryset:
            if not issue.return_date:
                issue.return_date = datetime.date.today()
                issue.save(update_fields=['return_date'])  # Сохраняем return_date
                
                if issue.is_web:
                    issue.book.web_amount = F('web_amount') + 1
                    issue.book.save(update_fields=['web_amount'])
                else:
                    issue.book.amount = F('amount') + 1
                    issue.book.save(update_fields=['amount'])
    actions = [mark_as_returned]


admin.site.register(IssueOfBooks, IssueOfBooksAdmin)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Publisher)

