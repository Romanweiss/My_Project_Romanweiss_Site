# Romanweiẞ Site

Полнофункциональный сайт фотографа и экспедиционного сторителлинга на Django + React.

## 1. Что важно сразу

- Основной пользовательский сайт: `http://localhost:5173/`
- Backend (API + admin): `http://localhost:8000/`
- Django здесь используется как источник контента/переводов и API-слой.
- React/Vite рендерит интерфейс и получает данные с Django API.

### Почему кажется, что «две версии сайта»

Это ожидаемо в dev-режиме:

- `:5173` — фронтенд (красивый UI, который вы редактируете как сайт).
- `:8000` — backend-сервис (админка, API, health-check; не «витрина»).

## 2. Текущая архитектура

### Backend (Django)

Роль:

- хранение контента, переводов, навигации, страниц и медиа-метаданных;
- управление контентом через Django Admin;
- REST API для фронтенда;
- хранение обращений из контактной формы.

Ключевые сущности в `content`:

- `SiteSettings`
- `SiteText`
- `Language`
- `TranslationKey`, `Translation`
- `Page`, `PageSection`, `HeroSection`, `SectionImage`
- `Menu`, `MenuItem`, `NavigationItem`
- `Expedition`, `ExpeditionMedia`, `Category`, `Story`
- `MediaAsset`

Отдельно в `api`:

- `ContactMessage`

### Frontend (React + Vite)

Роль:

- загрузка локализованных данных с `/api/...`;
- рендер страниц/секций/карточек без жестко зашитого контента;
- клиентская навигация по slug-маршрутам;
- переключение языка с синхронизацией в query и cookie.

## 3. Технологический стек

- Python `3.12` (Docker image `python:3.12-slim`)
- Django `>=5.0,<6.0`
- Django REST Framework
- PostgreSQL `16` (Docker image `postgres:16-alpine`)
- React `18`
- Vite `5`
- Docker + Docker Compose

## 4. Структура проекта

```text
backend/
  api/
  content/
  config/
  manage.py
frontend/
  src/
  vite.config.ts
docker-compose.yml
README.md
```

## 5. Запуск локально (через Docker)

### Требования

- Docker
- Docker Compose

### Шаги

1. Убедитесь, что есть файл `.env` в корне (пример ниже).
2. Запустите проект:

```bash
docker compose up --build
```

3. Откройте:

- фронтенд: `http://localhost:5173/`
- админка: `http://localhost:8000/admin/`

Примечание: обычно миграции применяются автоматически командой backend-контейнера при старте.

### Пример `.env`

```env
POSTGRES_DB=romanweiss
POSTGRES_USER=romanweiss
POSTGRES_PASSWORD=romanweiss

DJANGO_SECRET_KEY=dev-secret-key-change-me
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5173
```

### Полезные команды (только через контейнер)

```bash
# Проверка Django
docker compose run --rm backend python manage.py check

# Ручной прогон миграций (если нужно)
docker compose run --rm backend python manage.py migrate

# Создать администратора
docker compose exec backend python manage.py createsuperuser
```

## 6. URL и API

### Основные URL

- `http://localhost:5173/` — пользовательский интерфейс
- `http://localhost:8000/admin/` — Django Admin
- `http://localhost:8000/api/health/` — health endpoint

### Основные API endpoint'ы

- `GET /api/content/?lang=en|ru|zh`
- `GET /api/navigation/?lang=en|ru|zh`
- `GET /api/pages/<slug>/?lang=en|ru|zh`
- `GET /api/expeditions/?lang=en|ru|zh`
- `GET /api/stories/?lang=en|ru|zh`
- `POST /api/contact-messages/`
- `POST /api/i18n/set-language/`
- `GET /api/v1/bootstrap/?lang=en|ru|zh`

Также доступны `v1` и legacy-роуты для обратной совместимости.

## 7. Маршруты фронтенда

- `/` — главная
- `/expeditions/` — индекс экспедиций
- `/expeditions/:slug/` — детальная страница экспедиции
- `/<page-slug>/` — контентные страницы из CMS

## 8. Мультиязычность (i18n)

Текущие языки:

- `en` (по умолчанию)
- `ru`
- `zh`

Как работает:

- значения берутся из контентных сущностей и словарей переводов в БД;
- язык учитывается в API (`?lang=`) и cookie;
- при отсутствии перевода используется fallback на `en`.

Как добавить новый язык:

1. Добавьте язык в `Language` (админка) и при необходимости в `LANGUAGES` в Django settings.
2. Заполните переводы для `SiteText`, контентных сущностей и `Translation`.
3. Проверьте ответы API с `?lang=<new_code>`.
4. Проверьте отображение в переключателе языков на фронтенде.

## 9. Управление контентом (админка)

В админке можно управлять:

- брендом и общими настройками (`SiteSettings`);
- меню и ссылками (`Menu`, `MenuItem`, `NavigationItem`);
- страницами и секциями (`Page`, `PageSection`, `HeroSection`);
- экспедициями и их медиа-блоками (`Expedition`, `ExpeditionMedia`);
- категориями и историями (`Category`, `Story`);
- переводами и языками (`Language`, `TranslationKey`, `Translation`, `SiteText`).

Фото/видео для визуальных блоков рекомендуется поддерживать именно через админку Django.

## 10. Замечания по разработке

- Не изменять написание бренда `Romanweiẞ`.
- Избегать хардкода пользовательских текстов в React-компонентах.
- Ссылки и маршруты держать относительными, без жестких абсолютных путей там, где это не требуется.
- Для локального запуска используйте `docker compose up --build`.

## 11. Где выложить в общий доступ бесплатно

Ниже практичные варианты для бесплатной публикации (лимиты могут меняться):

### A) Просто открыть проект/README публично

1. GitHub (публичный репозиторий, бесплатно)
   - https://github.com/pricing

Это минимальный и самый быстрый способ открыть README и исходники для всех.

### B) Публичный хостинг фронтенда (статический/SPA)

1. GitHub Pages
   - https://docs.github.com/en/pages/getting-started-with-github-pages
2. Vercel (Hobby)
   - https://vercel.com/pricing
3. Netlify (Free)
   - https://www.netlify.com/pricing/
4. Cloudflare Pages (Free)
   - https://pages.cloudflare.com/

### C) Полный стек (Django + БД + frontend)

1. Render (есть бесплатные опции/ограничения)
   - https://render.com/docs/free
2. Railway (бесплатные лимиты/кредиты зависят от тарифа)
   - https://docs.railway.com/reference/pricing

Рекомендация для старта без оплаты:

- код и README держать в публичном GitHub;
- frontend — Vercel/Netlify/Cloudflare Pages;
- backend + БД — Render (или Railway при подходящих лимитах).

Перед публикацией проверьте актуальные ограничения и «sleep»/квоты на выбранной платформе.

## 12. Лицензирование и публикация

Если планируется публичный релиз, добавьте в репозиторий:

- `LICENSE` (например, MIT),
- `CONTRIBUTING.md` (по желанию),
- актуальный `.env.example` без секретов.
