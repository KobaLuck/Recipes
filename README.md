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

## GitHub Actions

При push и pull request запускаются проверки кода. Автоматического
развёртывания нет: проект сейчас не размещён на сервере.

Когда появится сервер, настройте секреты Docker Hub и SSH в GitHub,
откройте **Actions → CI and manual deployment → Run workflow**
и явно включите **deploy**. Без этой отметки образы не публикуются,
подключение к серверу и уведомления не выполняются.
