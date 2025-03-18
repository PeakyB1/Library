from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from engine.models import Book
from rest_framework.views import APIView
from rest_framework.response import Response
import fb2reader
class fb2_parser(fb2reader.fb2book):
    def get_translators(self):
        translators = []
        for translator in self.soup.find_all('translator'):
            first_name = translator.find('first-name').text
            last_name = translator.find('last-name').text
            if first_name != None:
                translatorsFL = first_name + " " + last_name    
                translators.append(translatorsFL)
        return translators
# Create your views here.
class EngineAPIView(APIView):
    def get(self, request, id):
        file = Book.objects.get(id=id).fb2file
        book = fb2_parser(file.path)
        title = book.get_title()
        identifier = book.get_identifier()
        authors = Book.objects.get(id=id).author.first_name + " " + Book.objects.get(id=id).author.last_name
        translators = book.get_translators()
        series = book.get_series()
        lang = book.get_lang()
        description = book.get_description()
        # tags = book.get_tags()
        isbn = book.get_isbn()
        cover_image = Book.objects.get(id=id).cover_url.replace('\\', '/')
        return Response({
            'Название': title,
            'Идентификатор': identifier,
            'Авторы': authors,
            'Переводчики': translators,
            'Серия': series,
            'Язык': lang,
            'Описание': description,
            # 'Теги': tags,
            'ISBN': isbn,
            'Обложка': cover_image
        })