# Library Management System

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
StaniSlave
