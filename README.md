# Electronic Library 

Проект создан для поиска, чтения и добавления книг с возможностью управления избранным и личным кабинетом пользователя.

## Требования

Docker и Docker Compose должны быть установлены.

## Установка и запуск

Клонируйте репозиторий и перейдите в папку проекта:
```bash
git clone git@github.com:MrGosling/library_project.git
cd library_project
```

Создайте файл `.env` на основе примера:
```bash
cp .env.example .env
```

Запустите проект:
```bash
docker compose up --build
```

При запуске автоматически применятся миграции и поднимется база данных PostgreSQL.

Сервер будет доступен по адресу: http://localhost:8000

## API Эндпоинты

Базовый URL: `http://localhost:8000/api/v1`

### Google Books
- `GET /google_books` — Поиск книг в Google Books.
  - Параметры: `query` (строка поиска).

### Авторы (Authors)
- `GET /authors` — Список авторов. Поддерживает фильтрацию `search`, а также `limit` и `offset`.
- `GET /authors/{author_id}` — Получение информации об авторе по ID.
- `POST /authors` — Создание нового автора.
- `PATCH /authors/{author_id}` — Обновление информации об авторе.
- `DELETE /authors/{author_id}` — Удаление автора.

### Категории (Categories)
- `GET /categories/` — Список всех категорий.
- `GET /categories/{category_id}` — Получение категории по ID.
- `POST /categories/` — Создание новой категории.
- `DELETE /categories/{category_id}` — Удаление категории.

### Жанры (Genres)
- `GET /genres/` — Список всех жанров.
- `GET /genres/{genre_id}` — Получение жанра по ID.
- `POST /genres/` — Создание нового жанра.
- `DELETE /genres/{genre_id}` — Удаление жанра.

### Пользователи (Users)
- `GET /users/` — Список всех пользователей.
- `GET /users/{user_id}` — Получение пользователя по ID.

### Служебные
- `GET /health` — Проверка работоспособности API.

## Зависимости

Установлены автоматически при сборке Docker-образа из `requirements.txt`.

## Цель проекта

Код написан в образовательных целях студентами ТюмГУ.


## AI setup

Проект использует локальную LLM через Ollama.
На данный момент используется модель размером ~2GB.

Первый запуск:
```bash
docker compose up -d ollama
docker compose exec ollama ollama pull qwen2.5:3b
docker compose up -d --build
```

Обычный запуск:
```bash
docker compose up -d
```

Не рекомендуется использовать:
```bash
docker compose down -v
```
так как эта команда удалит volume с моделью.
