from rest_framework import serializers
from engine.models import Genre, IssueOfBooks, Book, TocBook


class IssueOfBooksSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="book.title", read_only=True)
    author = serializers.CharField(source="book.author", read_only=True)
    issue_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    return_date = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M", allow_null=True, read_only=True
    )

    class Meta:
        model = IssueOfBooks
        fields = [
            "id",
            "issue_date",
            "return_date",
            "book",
            "title",
            "author",
            "reader",
            "is_web",
        ]
        read_only_fields = ("is_web", "book")


class BookListSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "cover",
            "file",
            "web_amount",
        ]
        depth = 1

    def get_file(self, obj):
        return True if obj.epub else False


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class BookDetailSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        depth = 1
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "year",
            "genre",
            "amount",
            "web_amount",
            "publisher",
            "summary",
            "cover",
            "file",
        ]

    def get_file(self, obj):
        return True if obj.epub else False


class TocSerializer(serializers.ModelSerializer):
    class Meta:
        model = TocBook
        fields = ["toc"]
