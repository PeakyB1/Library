from pathlib import Path

from ebooklib import epub
from ebooklib import ITEM_IMAGE
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from .models import BookChapter, TocBook

private_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)


class EpubImportService:

    def __init__(self, book):
        self.book = book
        self.storage = private_storage
        self.book_root = Path("books") / str(book.id)
        self.chapters_root = self.book_root / "chapters"
        self.images_root = self.book_root / "images"

    def parse_and_save(self, epub_path):
        epub_book = epub.read_epub(epub_path)
        self._save_toc(epub_book)
        self._save_images(epub_book)
        self._save_chapters(epub_book)

    def _save_toc(self, epub_book):
        toc_data = self._normalize_toc(epub_book.toc)

        TocBook.objects.update_or_create(
            book=self.book,
            defaults={
                "toc": toc_data,
            },
        )

    def _save_images(self, epub_book):
        for item in epub_book.get_items_of_type(ITEM_IMAGE):
            # Используем Path для безопасного извлечения имени файла вместо os.path.basename
            filename = Path(item.file_name).name
            if not filename:
                continue
            
            target_path = str(self.images_root / filename)
            self._save_bytes(target_path, item.get_content())

    def _save_chapters(self, epub_book):
        chapter_items = []

        for spine_item in epub_book.spine:
            item_id = spine_item[0]
            item = epub_book.get_item_with_id(item_id)
            if item and isinstance(item, epub.EpubHtml):
                chapter_items.append(item)

        for number, item in enumerate(chapter_items, start=1):
            filename = Path(item.file_name).name
            if not filename:
                continue

            file_title, _ = Path(filename).stem, Path(filename).suffix
            body = item.get_body_content()
            html_bytes = body if isinstance(body, bytes) else body.encode("utf-8")

            chapter = BookChapter(
                book=self.book,
                title=file_title,
                number=number
            )
            chapter.file.save(filename, ContentFile(html_bytes), save=True)

    def _normalize_toc(self, toc):
        normalized = []
        for node in toc:
            if isinstance(node, tuple) and len(node) == 2:
                link, children = node
                normalized.append(
                    {
                        "title": getattr(link, "title", ""),
                        "href": getattr(link, "href", ""),
                        "children": self._normalize_toc(children),
                    }
                )
            elif hasattr(node, "href"):
                normalized.append(
                    {
                        "title": getattr(node, "title", ""),
                        "href": getattr(node, "href", ""),
                    }
                )
        return normalized

    def _save_bytes(self, path, data):
        if self.storage.exists(path):
            self.storage.delete(path)
        self.storage.save(path, ContentFile(data))