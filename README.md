# BIBALARY Management System

## Описание

Это веб-приложение на Django для управления библиотекой. Оно позволяет работать с книгами, пользователями и выдачей литературы.

## Функции
- Управление пользователями
- Работа с каталогом книг
- Оформление выдачи и возврата книг
- Панель администратора для управления библиотекой

## Установка
### 1. Клонирование репозитория
```sh
git clone https://github.com/yourusername/Library.git
cd Library
```

### 2. Создание и активация виртуального окружения
```sh
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей
```sh
pip install -r requirements.txt
```

### 4. Применение миграций базы данных
```sh
python manage.py migrate
```

### 5. Создание суперпользователя
```sh
python manage.py createsuperuser
```

### 6. Запуск сервера разработки
```sh
python manage.py runserver
```

## Использование
После запуска сервера приложение будет доступно по адресу: `http://127.0.0.1:8000/`.

- Панель администратора: `http://127.0.0.1:8000/admin/`
- Основные страницы доступны через навигационное меню.

## Технологии
- Python 3
- Django
- SQLite (по умолчанию)
- HTML, CSS

## Автор
꧁༺ 𝓢𝓽𝓪𝓷𝓲𝓼𝓵𝓪𝓿𝓮 ༻꧂

```
Library
├─ 📁API
│  ├─ 📁migrations
│  │  └─ 📄__init__.py
│  ├─ 📁__pycache__
│  ├─ 📄admin.py
│  ├─ 📄apps.py
│  ├─ 📄models.py
│  ├─ 📄tests.py
│  ├─ 📄urls.py
│  ├─ 📄views.py
│  └─ 📄__init__.py
├─ 📁engine
│  ├─ 📁migrations
│  │  ├─ 📁__pycache__
│  │  ├─ 📄0001_initial.py
│  │  ├─ 📄0002_alter_author_options_alter_book_options_and_more.py
│  │  ├─ 📄0003_alter_issueofbooks_reader_delete_reader.py
│  │  ├─ 📄0004_book_fb2file.py
│  │  └─ 📄__init__.py
│  ├─ 📁__pycache__
│  ├─ 📄admin.py
│  ├─ 📄apps.py
│  ├─ 📄forms.py
│  ├─ 📄models.py
│  ├─ 📄tests.py
│  ├─ 📄urls.py
│  ├─ 📄views.py
│  └─ 📄__init__.py
├─ 📁Library
│  ├─ 📁__pycache__
│  ├─ 📄asgi.py
│  ├─ 📄settings.py
│  ├─ 📄urls.py
│  ├─ 📄wsgi.py
│  └─ 📄__init__.py
├─ 📁media
│  ├─ 📄1984.fb2
│  ├─ 📄Большие надежды.fb2
│  ├─ 📄Война и мир.fb2
│  ├─ 📄Гарри Поттер и философский камень.fb2
│  ├─ 📄Гордость и предубеждение.fb2
│  ├─ 📄Преступление и наказание.fb2
│  ├─ 📄Приключения Гекльберри Финна.fb2
│  ├─ 📄Скотный двор.fb2
│  ├─ 📄Старик и море.fb2
│  ├─ 📄Убийство в Восточном экспрессе.fb2
│  └─ 📄Хоббит.fb2
├─ 📁output
│  └─ 📄body
├─ 📁static
│  ├─ 📁covers
│  │  ├─ 📄0j9cxt3xqpuf4jhwipnclnc487fqr9dm.jpg
│  │  ├─ 📄1003862713.jpg
│  │  ├─ 📄6008637185.jpg
│  │  ├─ 📄6008814707.jpg
│  │  ├─ 📄6049401543.jpg
│  │  ├─ 📄6049403543.jpg
│  │  ├─ 📄6091641684.jpg
│  │  ├─ 📄6353881258.jpg
│  │  ├─ 📄6792956659.jpg
│  │  ├─ 📄cover1__w820.jpg
│  │  └─ 📄d62ec3e42af24d87.jpg
│  ├─ 📁css
│  │  ├─ 📄reset.css
│  │  └─ 📄styles.css
│  ├─ 📁fonts
│  │  ├─ 📄wellwaitfree_regular.eot
│  │  ├─ 📄wellwaitfree_regular.svg
│  │  ├─ 📄wellwaitfree_regular.ttf
│  │  ├─ 📄wellwaitfree_regular.woff
│  │  └─ 📄wellwaitfree_regular.woff2
│  └─ 📁images
│     ├─ 📄60c7ca12-4953-45ec-8505-56255dfca560.png
│     ├─ 📄back1.png
│     ├─ 📄back2.png
│     ├─ 📄back3.png
│     ├─ 📄back4.png
│     ├─ 📄back5.png
│     ├─ 📄book.png
│     ├─ 📄edgar.png
│     ├─ 📄icons8-поиск-49.png
│     ├─ 📄lenin.png
│     ├─ 📄search-icon.png
│     └─ 📄Без имени-1.psd
├─ 📁templates
│  ├─ 📄about.html
│  ├─ 📄account.html
│  ├─ 📄base.html
│  ├─ 📄book.html
│  ├─ 📄contact.html
│  ├─ 📄index.html
│  ├─ 📄login.html
│  ├─ 📄register.html
│  ├─ 📄search.html
│  └─ 📄test.html
├─ 📁users
│  ├─ 📁migrations
│  │  ├─ 📁__pycache__
│  │  └─ 📄__init__.py
│  ├─ 📁__pycache__
│  ├─ 📄admin.py
│  ├─ 📄apps.py
│  ├─ 📄forms.py
│  ├─ 📄models.py
│  ├─ 📄tests.py
│  ├─ 📄urls.py
│  ├─ 📄views.py
│  └─ 📄__init__.py
├─ 📄.gitignore
├─ 📄fb2_parser.py
├─ 📄manage.py
├─ 📄README.md
└─ 📄requirements.txt
```
