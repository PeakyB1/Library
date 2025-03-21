from rest_framework import serializers
from .models import Book


def get(id):
    data = Book.objects.all()
    print(type(data))
class BookSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    author = serializers.CharField(max_length=100)
    genre = serializers.CharField(max_length=100)
    year = serializers.IntegerField()
    amount = serializers.IntegerField()