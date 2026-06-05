import re
import os
import time
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import urllib.error
import tempfile
import django
from django.core.files.base import ContentFile

# Настройки стабильности
TIMEOUT_SECONDS = 30  # Тайм-аут на один запрос
MAX_RETRIES = 5       # Количество попыток при ошибке сети/тайм-ауте
RETRY_DELAY = 3       # Базовая задержка между попытками (в секундах)

# Префиксы метаданных, которые часто висят в конце отдельными строками
META_PREFIXES = (
    "год издания:", 
    "формат:", 
    "язык:", 
    "размер:", 
    "добавлен:",
    "isbn:",
    "перевод:",
    "скачиваний:",
    "просмотров:",
    "скачано:",
    "серия:"
)

# База стоп-слов для проверки строк с конца
STOP_WORDS = [
    "издательский макет",
    "формате pdf",
    "сохранен издательский",
    "оцифровка",
    "сканирование",
    "копирование запрещено",
    "количество скачиваний",
    "макет книги"
]

# Очиститель HTML-тегов от мусора в аннотациях
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paragraphs = []
        self.current_p = []

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br', 'div') and self.current_p:
            self.paragraphs.append("".join(self.current_p).strip())
            self.current_p = []

    def handle_endtag(self, tag):
        if tag in ('p', 'div') and self.current_p:
            self.paragraphs.append("".join(self.current_p).strip())
            self.current_p = []

    def handle_data(self, data):
        if data.strip():
            self.current_p.append(data.strip() + " ")

    def get_clean_text(self):
        if self.current_p:
            self.paragraphs.append("".join(self.current_p).strip())

        valid_paragraphs = [p for p in self.paragraphs if p.strip()]

        while valid_paragraphs:
            last_p = valid_paragraphs[-1].lower().strip()
            
            is_stop_word = any(word in last_p for word in STOP_WORDS)
            is_metadata = any(last_p.startswith(prefix) for prefix in META_PREFIXES)

            if is_stop_word or is_metadata:
                valid_paragraphs.pop()
            else:
                break

        text = "\n\n".join(valid_paragraphs)
        text = re.sub(r'\[/?(b|i|u)\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[ \t\xa0]{2,}', ' ', text)

        return text.strip()


def clean_html(html_text):
    if not html_text:
        return "Нет аннотации"
    parser = HTMLTextExtractor()
    parser.feed(html_text)
    return parser.get_clean_text()


def clean_title(text):
    """Выкидывает из названия все круглые и квадратные скобки вместе с содержимым ([litres], (СИ) и т.д.)"""
    if not text:
        return "Без названия"
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def fix_url(base_url, link_url):
    if not link_url:
        return None
    if link_url.startswith("http://") or link_url.startswith("https://"):
        return link_url
    
    parsed_base = urlparse(base_url)
    domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
    
    if link_url.startswith("/"):
        return domain + link_url
    return domain + "/" + link_url


def fetch_url_with_retry(url):
    """Качает данные по URL с повторными попытками при тайм-аутах или ошибках сети"""
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionResetError) as e:
            current_delay = RETRY_DELAY * attempt
            print(f"  ⚠ [Попытка {attempt}/{MAX_RETRIES}] Ошибка сети/Таймаут при обращении к {url}: {e}")
            if attempt == MAX_RETRIES:
                print("  ✗ Все попытки исчерпаны.")
                raise e
            print(f"  Ожидание {current_delay} сек перед следующей попыткой...")
            time.sleep(current_delay)


# ===== ФУНКЦИИ ДЛЯ СОХРАНЕНИЯ В БД =====

def download_cover(cover_url):
    if not cover_url:
        return None
    try:
        cover_data = fetch_url_with_retry(cover_url)
        if not cover_data:
            return None
            
        filename = os.path.basename(urlparse(cover_url).path)
        if not filename or not os.path.splitext(filename)[1]:
            filename = f"cover.jpg"
        
        return ContentFile(cover_data, name=filename)
    except Exception as e:
        print(f"  ✗ Ошибка при загрузке обложки (пропущено): {e}")
        return None


def download_epub(epub_url):
    if not epub_url:
        return None
    try:
        epub_data = fetch_url_with_retry(epub_url)
        if not epub_data:
            return None
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.epub')
        temp_file.write(epub_data)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"  ✗ Ошибка при загрузке EPUB (пропущено): {e}")
        return None


def save_book_to_db(title, authors_str, annotation, cover_url, epub_url):
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Library.settings')
        django.setup()
    
    from engine.models import Book, Author, Genre, Publisher
    from engine.services import EpubImportService
    
    try:
        author_name = authors_str.strip() if authors_str else "Неизвестный автор"
        author, _ = Author.objects.get_or_create(name=author_name)
        
        genre, _ = Genre.objects.get_or_create(name="Неизвестный жанр")
        publisher, _ = Publisher.objects.get_or_create(name="Неизвестный издатель")
        
        book = Book.objects.create(
            title=title,
            author=author,
            year=2026,
            genre=genre,
            amount=1,
            web_amount=1,
            publisher=publisher,
            summary=annotation
        )
        
        cover_file = download_cover(cover_url)
        if cover_file:
            book.cover.save(cover_file.name, cover_file, save=False)
        
        book.save()
        print(f"  ✓ Книга сохранена в БД (ID: {book.id})")
        
        epub_path = download_epub(epub_url)
        if epub_path:
            with open(epub_path, 'rb') as f:
                filename = os.path.basename(urlparse(epub_url).path)
                if not os.path.splitext(filename)[1]:
                    filename = f"{filename}.epub"
                book.epub.save(filename, ContentFile(f.read()), save=True)
            
            service = EpubImportService(book)
            service.parse_and_save(epub_path)
            print(f"  ✓ EPUB обработан и главы сохранены")
            os.unlink(epub_path)
        else:
            print(f"  ✗ EPUB не был загружен")
        
        return book
    except Exception as e:
        print(f"  ✗ Критическая ошибка при сохранении книги '{title}': {e}")


# ===== ОСНОВНОЙ ЦИКЛ С ПАГИНАЦИЕЙ =====

current_url = "https://flibusta.is/opds/sequencebooks/39942"
page_number = 1

while current_url:
    print(f"\n[{page_number}] Загрузка страницы: {current_url} ...")
    
    try:
        # Качаем XML страницы с защитой от тайм-аута
        xml_data = fetch_url_with_retry(current_url)
        
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # Обрабатываем все книги на текущей странице
        for entry in root.findall("atom:entry", ns):
            title_node = entry.find("atom:title", ns)
            raw_title = title_node.text if title_node is not None else "Без названия"
            title = clean_title(raw_title)

            authors = []
            for author_node in entry.findall("atom:author", ns):
                name_node = author_node.find("atom:name", ns)
                if name_node is not None:
                    authors.append(name_node.text)
            authors_str = ", ".join(authors) if authors else "Автор не указан"

            content_node = entry.find("atom:content", ns)
            raw_annotation = (
                content_node.text if content_node is not None else ""
            )
            annotation = clean_html(raw_annotation)

            epub_url = None
            cover_url = None

            for link in entry.findall("atom:link", ns):
                link_type = link.get("type")
                link_rel = link.get("rel")

                if link_type == "application/epub+zip":
                    epub_url = fix_url(current_url, link.get("href"))
                elif link_rel == "http://opds-spec.org/image":
                    cover_url = fix_url(current_url, link.get("href"))

            print(f"\nНазвание: {title}")
            print(f"Авторы:  {authors_str}")
            print(f"Ссылка на EPUB: {epub_url}")
            
            # Ошибки скачивания конкретной книги не должны прерывать пагинацию страниц
            save_book_to_db(title, authors_str, annotation, cover_url, epub_url)
            print("-" * 40)

        # Поиск ссылки на следующую страницу (пагинация)
        next_url = None
        for link in root.findall("atom:link", ns):
            if link.get("rel") == "next":
                next_url = fix_url(current_url, link.get("href"))
                break
        
        if next_url:
            current_url = next_url
            page_number += 1
            time.sleep(2)  # Пауза между страницами
        else:
            print("\nДостигнута последняя страница. Парсинг завершен.")
            current_url = None

    except Exception as e:
        # Если даже после всех попыток страница не загрузилась, аккуратно останавливаемся без краша скрипта
        print(f"\n✗ Не удалось загрузить или распарсить страницу {current_url} после нескольких попыток: {e}")
        print("Работа скрипта аварийно приостановлена во избежание потери прогресса.")
        break