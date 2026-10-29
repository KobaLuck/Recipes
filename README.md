# Recipes · Foodgram

Платформа для рецептов: публикации, теги, ингредиенты, подписки, избранное и общий список покупок.

**Python · Django · DRF · React · PostgreSQL · Docker**

## Быстрый старт

```bash
git clone https://github.com/KobaLuck/Recipes.git
cd Recipes
cp .env.example .env
# Заполните .env для своей среды
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

Локальный Docker Compose собирает сервисы из исходного кода; production-конфигурация использует готовые образы. Веб-интерфейс доступен на `http://localhost:7000`, API — `/api/`. Создать администратора: `docker compose exec backend python manage.py createsuperuser`. Спецификация: `docs/openapi-schema.yml`.

## Структура

- `backend/` — серверная часть.
- `frontend/` — веб-интерфейс.
- `docs/` — документация.
- `infra/` — конфигурация инфраструктуры.
- `postman_collection/` — коллекции запросов.

---

[Никита Казанцев](https://github.com/KobaLuck) · [Все публичные проекты](https://github.com/KobaLuck?tab=repositories)
