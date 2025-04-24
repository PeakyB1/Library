from rest_framework import serializers
from engine.models import Genre, IssueOfBooks, Book
import fb2reader


class fb2_parser(fb2reader.fb2book):
    def get_translators(self):
        translators = []
        for translator in self.soup.find_all("translator"):
            first_name = translator.find("first-name").text
            last_name = translator.find("last-name").text
            if first_name != None:
                translatorsFL = first_name + " " + last_name
                translators.append(translatorsFL)
        return translators


class IssueOfBooksSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(read_only=True)
    cover = serializers.ImageField(source="book.cover", read_only=True)
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
            "cover",
            "reader",
            "is_web",
        ]


class BookListSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            # "year",
            # "genre",
            # "publisher",
            "cover",
            # "amount",
            # "web_amount",
            "file",
        ]
        depth = 1

    def get_file(self, obj):
        return True if obj.fb2file else False


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class BookDetailSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    translators = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    isbn = serializers.SerializerMethodField()
    # identifier = serializers.SerializerMethodField()
    # series = serializers.SerializerMethodField()

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
            "translators",
            "language",
            "isbn",
        ]

    def get_file(self, obj):
        return bool(obj.fb2file)

    def parse_fb2(self, obj):
        if not obj.fb2file:
            return None
        return fb2_parser(obj.fb2file.path)

    def get_translators(self, obj):
        book = self.parse_fb2(obj)
        return book.get_translators() if book else None

    def get_identifier(self, obj):
        book = self.parse_fb2(obj)
        return book.get_identifier() if book else None

    def get_language(self, obj):
        book = self.parse_fb2(obj)
        return book.get_lang() if book else None

    def get_isbn(self, obj):
        book = self.parse_fb2(obj)
        return book.get_isbn() if book else None

    def get_series(self, obj):
        book = self.parse_fb2(obj)
        return book.get_series() if book else None
