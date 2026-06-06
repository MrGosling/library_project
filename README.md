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

3. Проект разделён на два compose-файла:

- `docker-compose.dev.yml` — разработка (live-reload backend через `uvicorn
  --reload`, отдельный сервис фронтенда с Vite dev-сервером и HMR на :5173,
  gateway на :3000, открытые порты db и backend);
- `docker-compose.prod.yml` — продакшен (без reload, несколько воркеров,
  статика фронтенда собрана в образ gateway, наружу открыт только gateway
  на :80, db и backend во внутренней сети, restart-политики и healthcheck).

4. Первый запуск (с загрузкой AI-модели). Подставьте нужный compose-файл
   через флаг `-f` (примеры ниже для разработки):
```bash
# Запуск Ollama
docker compose -f docker-compose.dev.yml up -d ollama

# Загрузка модели (по умолчанию qwen2.5:3b)
docker compose -f docker-compose.dev.yml exec ollama ollama pull qwen2.5:3b

# Разработка: запуск всего проекта
docker compose -f docker-compose.dev.yml up -d --build

# Продакшен: запуск всего проекта
docker compose -f docker-compose.prod.yml up -d --build
```

При запуске автоматически применяются миграции и выполняется инициализация базы данных (создание суперпользователя и начальных данных).

В режиме разработки:
- Фронтенд с HMR (Vite): http://localhost:5173 — используйте для разработки фронта
- Приложение (через gateway, prod-сборка статики): http://localhost:3000
- API: http://localhost:8000, Swagger: http://localhost:8000/docs

В режиме продакшена:
- Приложение и API (через gateway): http://localhost (порт 80)
- API напрямую наружу не публикуется

## Фронтенд и Gateway

Веб-приложение на React (Vite) находится в каталоге `frontend/`.

Стек: **React 18**, **React Router** (маршрутизация), **Axios** (работа с API),
**Service Worker** (офлайн-режим и кэширование), сборка через **Vite**.

Раздачей статики и маршрутизацией запросов занимается отдельный сервис
**gateway** (nginx) в каталоге `gateway/`. Он является единой точкой входа:
отдаёт собранную статику фронтенда и проксирует запросы `/api` на сервис
`backend`. Образ gateway собирается из корня проекта (`gateway/Dockerfile`):
на этапе сборки собирается фронтенд из `frontend/`, затем статика копируется
в nginx.

Список разрешённых для CORS источников задаётся переменной `CORS_ORIGINS_STR`
в `.env` (значения через запятую). По умолчанию включает `http://localhost:5173`,
`http://localhost:3000` и `http://localhost`.

Страницы:
- `/` — главная (информация о приложении);
- `/login`, `/register` — авторизация и регистрация;
- `/books` — каталог книг (поиск, фильтры по автору и категории, пагинация,
  добавление книг);
- `/books/:id` — страница книги (описание, рейтинг, отзывы, избранное);
- `/favorites` — избранное;
- `/profile` — личный кабинет (статистика, смена пароля).

### Запуск в Docker

Gateway (вместе со статикой фронтенда) поднимается вместе со всем проектом:
- разработка: `docker compose -f docker-compose.dev.yml up -d --build` → http://localhost:3000
- продакшен: `docker compose -f docker-compose.prod.yml up -d --build` → http://localhost

### Разработка фронтенда с HMR

В dev-режиме поднимается отдельный сервис `frontend` с Vite dev-сервером:
изменения в `./frontend` подхватываются автоматически (HMR), пересборка не нужна.

- Адрес dev-сервера: http://localhost:5173 (запросы `/api` проксируются на
  `backend`).
- Внутри контейнера цель прокси задаётся переменной `VITE_PROXY_TARGET`
  (`http://backend:8000`); при запуске Vite вне Docker используется
  `http://localhost:8000` по умолчанию.
- Gateway на :3000 отдаёт собранную статику (prod-сборку) — удобно для
  проверки итогового бандла.

Запуск Vite вне Docker (опционально):
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
npm run build # production-сборка в каталог dist
```

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
