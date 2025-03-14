import xml.etree.ElementTree as ET
import os
import json
import fb2reader

class FB2Parser:
    def __init__(self, filename, page_size=1000, external_annotations=True):
        self.root = ET.parse(filename).getroot()
        self.cleanup()
        self.page_size = page_size  # Количество символов на одной условной странице
        self.external_annotations = external_annotations
        self.full_text = ""  # Полный текст книги для разделения на страницы

    def cleanup(self):
        """Удалить пространство имен из тегов XML для удобства парсинга."""
        for element in self.root.iter():
            element.tag = element.tag.partition('}')[-1]

    def is_flat(self):
        """Определить, содержит ли книга главы (flat == нет глав)."""
        return self.root.find('./body/section/section') is None

    def extract_full_text(self):
        """Извлечь весь текст книги в одну строку."""
        body = self.root.find('./body')
        if body is None:
            raise ValueError("FB2 файл не содержит текстовой части (body)")
        
        # Собрать весь текст внутри тега <body>
        self.full_text = "".join(body.itertext())
        return self.full_text

    def get_page(self, page_number):
        if not self.full_text:
            self.extract_full_text()
        start_index = self.page_size * (page_number - 1)
        end_index = start_index + self.page_size

        if start_index >= len(self.full_text):
            return {
                "error": f"Page {page_number} does not exist."
            }

        # Извлечь текст страницы
        page_content = self.full_text[start_index:end_index]

        # С разделением по строкам
        lines = page_content.split("\n")

        return {
            "page_number": page_number,
            "content": lines,  # Возврат массива строк
            "total_pages": (len(self.full_text) + self.page_size - 1) // self.page_size
    }


    def save_page_to_file(self, page_number, output_file):
        """
        Сохранить страницу в JSON-файл.
        :param page_number: Номер страницы, который нужно сохранить.
        :param output_file: Имя файла, в который будет записан результат.
        """
        # Получить данные страницы
        page_data = self.get_page(page_number)

        # Сохранить текст в JSON-файл с параметром ensure_ascii=False
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=4)  # indent=4 для удобного чтения
        print(f"Данные страницы {page_number} сохранены в файл: {output_file}")

class FixedFB2Book(fb2reader.fb2book):  
    def get_authors(self):
        authors = []  # Создаём пустой список, если авторов нет
        for author in getattr(self, "authors", []):  # Берём авторов из атрибута книги
            first_name = getattr(author, "first_name", "") or ""
            middle_name = getattr(author, "middle_name", "") or ""
            last_name = getattr(author, "last_name", "") or ""
            full_name = " ".join(filter(None, [first_name, middle_name, last_name]))
            authors.append(full_name)
        return authors if authors else ["Неизвестный автор"]  # Если авторов нет, пишем заглушку
if __name__ == "__main__":
    # parser = FB2Parser("gmn.fb2", page_size=4000)  # Установим, что одна страница = 1000 символов
    
    # # Сохранить страницу 1 в файл
    # parser.save_page_to_file(7, "page_7.json")

    file_path = 'media\Хоббит.fb2'
    book = FixedFB2Book(file_path)

    book.save_body_as_html(output_dir='output', output_file_name='body')
