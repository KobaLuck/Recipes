---

#  Foodgram

> Социальная сеть для создания и обмена рецептами. Позволяет добавлять рецепты в корзину для автоматического формирования списка покупок.

---

##  Сайт проекта

Рабочая версия доступна по адресу: [https://vikathebest.ddns.net](https://vikathebest.ddns.net)

---

##  Автор

**Казанцев Никита Игоревич**
**GitHub:** [https://github.com/KobaLuck](https://github.com/KobaLuck)

---

##  Технологический стек

* **Backend:** Python 3, Django 3.2.3, Django REST Framework 3.12.4, Djoser 2.1.0, django-filter 2.4.0, PyYAML 6.0, webcolors 1.11.1, Pillow 9.0.0, Gunicorn 20.1.0, psycopg2-binary 2.9.3
* **Frontend:** React 17.0.1 (SPA на Create React App)
* **База данных:** PostgreSQL 13
* **Сервер:** Nginx, Gunicorn
* **Контейнеризация:** Docker, Docker Compose
* **CI/CD:** GitHub Actions, DockerHub, автоматический деплой по SSH
* **Volumes:** pg\_data, static, media

---

##  CI/CD Pipeline

GitHub Actions на каждом `push` в репозиторий:

1. Проверка синтаксиса и линтинг — flake8
2. Юнит-тесты (при необходимости)
3. Сборка и пуш Docker-образов для backend, frontend и gateway на DockerHub
4. Автоматический деплой на удалённый сервер по SSH (для ветки `main`):

   * копирование `docker-compose.production.yml`
   * pull, down/up контейнеров
   * миграции и сбор статики
   * уведомления в Telegram при успехе и при сбое

---

##  Локальное развертывание через Docker

### 1. Клонирование репозитория

```bash
git clone https://github.com/KobaLuck/foodgram.git
cd foodgram
```

### 2. Подготовка `.env`

Создайте файл `.env` на основе `example.env`:

```bash
cp example.env .env
```

Пример содержимого `example.env`:

```ini
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_admin
POSTGRES_PASSWORD=145749449A
DB_HOST=db
DB_PORT=5432
DJANGO_KEY="somekey"
DJANGO_DEBUG=True
DJANGO_HOSTS="0.0.0.0,localhost,127.0.0.1,x.x.x.x"
```

### 3. Подъем контейнеров

```bash
docker-compose up --build -d
```

### 4. Подготовка базы и загрузка данных

```bash
docker-compose exec backend python manage.py migrate
```

Создание суперпользователя:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Загрузка фикстур:

```bash
docker-compose exec backend python manage.py loaddata ingredients.json
```

### 5. Сбор статики

```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

### 6. Доступ к приложению

* **Frontend:** [http://localhost](http://localhost)
* **API-документация:** [http://localhost/api/docs/](http://localhost/api/docs/)

---

##  Локальное развертывание **без Docker**

### 1. Клонирование репозитория

```bash
git clone https://github.com/KobaLuck/foodgram.git
cd foodgram
```

### 2. Создание и активация виртуального окружения

```bash
python -m venv venv
source venv/bin/activate    # или Windows: venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 4. Подготовка `.env`

```bash
cp example.env .env
```

### 5. Миграции и суперпользователь

```bash
python backend/manage.py migrate
python backend/manage.py createsuperuser
```

### 6. Импорт данных

```bash
python backend/manage.py loaddata ingredients.json
```

### 7. Запуск сервера

```bash
cd backend
python manage.py runserver
```

* **Backend (API):** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Frontend:** запустите отдельным `npm start` в папке `frontend` по инструкции React
* **API-документация:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

---

##  Документация API

После запуска доступна спецификация:

* **Redoc:** [http://localhost/api/docs/](http://localhost/api/docs/)

---

*Спасибо за использование Foodgram!*
