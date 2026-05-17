# Electronic Library 

Проект создан для поиска, чтения и добавления книг с возможностью управления избранным и личным кабинетом пользователя.

## Требования

Docker и Docker Compose должны быть установлены.

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone git@github.com:MrGosling/library_project.git
cd library_project
```

2. Создайте файл `.env` на основе примера (обязательно укажите настройки базы данных, Ollama, а также всех необходимых значений):
```bash
cp .env.example .env
```

3. Первый запуск (с загрузкой AI-модели):
```bash
# Запуск Ollama
docker compose up -d ollama

# Загрузка модели (по умолчанию qwen2.5:3b)
docker compose exec ollama ollama pull qwen2.5:3b

# Запуск всего проекта
docker compose up -d --build

# Запуск всего проекта с выводом в консоль
docker compose up --build
```

При запуске автоматически применяются миграции и выполняется инициализация базы данных (создание суперпользователя и начальных данных).

Сервер будет доступен по адресу: http://localhost:8000
Документация API (Swagger): http://localhost:8000/docs

## API Эндпоинты

Базовый URL: `http://localhost:8000/api/v1`

### Книги (Books)
- `GET /books` — Список всех книг.
- `GET /books/{book_id}` — Получение книги по ID.
- `POST /books` — Добавление новой книги (требуется `author_id`).
- `DELETE /books/{book_id}` — Удаление книги.

### Авторы (Authors)
- `GET /authors` — Список авторов. Поддерживает фильтрацию `search`, а также `limit` и `offset`.
- `GET /authors/{author_id}` — Получение информации об авторе по ID.
- `POST /authors` — Создание нового автора.
- `PATCH /authors/{author_id}` — Обновление информации об авторе.
- `DELETE /authors/{author_id}` — Удаление автора.

### Категории (Categories)
- `GET /categories` — Список всех категорий.
- `GET /categories/{category_id}` — Получение категории по ID.
- `POST /categories` — Создание новой категории.
- `DELETE /categories/{category_id}` — Удаление категории.

### Жанры (Genres)
- `GET /genres` — Список всех жанров.
- `GET /genres/{genre_id}` — Получение жанра по ID.
- `POST /genres` — Создание нового жанра.
- `DELETE /genres/{genre_id}` — Удаление жанра.

### Пользователи и Аутентификация (Users)
- `POST /users/register` — Регистрация нового пользователя.
- `POST /users/login` — Вход и получение токена.
- `POST /users/change-password` — Смена пароля.
- `POST /users/refresh-token` — Обновление токена.

### AI Рекомендации
- `POST /ai/recommendations` — Получение персональных рекомендаций на основе прочитанных книг.
- `GET /ai/health` — Проверка состояния сервиса Ollama.

### Внешние интеграции
- `GET /google_books` — Поиск книг через Google Books API.
  - Параметр: `query` (строка поиска).

### Служебные
- `GET /health` — Проверка работоспособности основного API.

## Разработка

Проект использует:
- **FastAPI** — веб-фреймворк.
- **SQLAlchemy 2.0** (async) — ORM.
- **PostgreSQL** — база данных.
- **Alembic** — миграции БД.
- **Ollama** — локальный запуск LLM для рекомендаций.
- **Pydantic v2** — валидация данных.
- **Ruff** — линтинг и форматирование кода.

## AI Setup

Проект использует локальную LLM через Ollama. 
Не рекомендуется использовать команду `docker compose down -v`, так как она удалит сохраненную модель в volume.

## Цель проекта

Код написан в образовательных целях студентами ТюмГУ.
