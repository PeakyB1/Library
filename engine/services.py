import json
import os

from ebooklib import epub
from ebooklib import ITEM_IMAGE, ITEM_DOCUMENT
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from .models import BookChapter, TocBook

private_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)


class EpubImportService:

    def __init__(self, book):
        self.book = book
        self.storage = private_storage
        self.book_root = os.path.join("books", str(book.id))
        self.chapters_root = os.path.join(self.book_root, "chapters")
        self.images_root = os.path.join(self.book_root, "images")

    def parse_and_save(self, epub_path):
        epub_book = epub.read_epub(epub_path)
        self._save_toc(epub_book)
        self._save_images(epub_book)
        self._save_chapters(epub_book)
        self._save_cover(epub_book)

    def _save_cover(self, epub_book):
        if self.book.cover:
            return
        cover_item = None

        for item in epub_book.get_items_of_type(ITEM_IMAGE):
            if "cover" in item.file_name.lower():
                cover_item = item
                break

        if cover_item:
            filename = os.path.basename(cover_item.file_name)
            content = cover_item.get_content()

            self.book.cover.save(
                filename,
                ContentFile(content),
                save=False
            )
        else:
            self.book.cover = None

        self.book.save(update_fields=["cover"])

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
            filename = os.path.basename(item.file_name)
            if not filename:
                continue
            target_path = os.path.join(self.images_root, filename)
            self._save_bytes(target_path, item.get_content())

    def _save_chapters(self, epub_book):
        chapter_items = []
        for item in epub_book.get_items_of_type(ITEM_DOCUMENT):
            if isinstance(item, epub.EpubHtml):
                chapter_items.append(item)

        for number, item in enumerate(chapter_items, start=1):
            title = self._get_title(item, number)
            body = item.get_body_content()
            html_bytes = body if isinstance(body, bytes) else body.encode("utf-8")
            filename = f"chapter-{number}.html"
            target_path = os.path.join(self.chapters_root, filename)
            self._save_bytes(target_path, html_bytes)
            BookChapter.objects.create(
                book=self.book,
                title=title,
                number=number,
                file=target_path,
            )

    def _get_title(self, item, number):
        if hasattr(item, "get_metas"):
            metas = item.get_metas() or []
            for meta in metas:
                if isinstance(meta, dict) and meta.get("name", "").lower() == "title":
                    return meta.get("content") or meta.get("value") or f"Глава {number}"
        if hasattr(item, "get_name"):
            name = item.get_name()
            if name:
                return (
                    os.path.splitext(os.path.basename(name))[0]
                    .replace("_", " ")
                    .title()
                )
        if hasattr(item, "file_name") and item.file_name:
            return (
                os.path.splitext(os.path.basename(item.file_name))[0]
                .replace("_", " ")
                .title()
            )
        return f"Глава {number}"

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
