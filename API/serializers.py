from rest_framework import serializers
from engine.models import Genre, IssueOfBooks, Book, TocBook


class IssueOfBooksSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(source="book.title", read_only=True)
    author = serializers.CharField(source="book.author", read_only=True)

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
        read_only_fields = ("is_web",)


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
            # "amount",
            # "web_amount",
            # "year",
            # "genre",
            # "publisher",
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
            # "translators",
            # "language",
            # "isbn",
        ]

    def get_file(self, obj):
        return bool(obj.epub)


class TocSerializer(serializers.ModelSerializer):
    class Meta:
        model = TocBook
        fields = ["toc"]
