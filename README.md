# Software Architecture Group 7

This project is a **Django-based book review platform** with modular apps for authors, books, reviews, and sales. It is fully containerized using Docker for easy setup.

---

## **Getting Started**

Clone the repository and navigate into the project folder:

```bash
git clone https://github.com/AlbertoZuiga/software-architecture-group-7.git
cd software-architecture-group-7
```

### Deployment Options

#### Option 1: Application + Database (without cache)

Build and start the containers using standard Docker Compose:

```bash
docker-compose up --build -d
```

This will start the application with PostgreSQL but without Redis cache.

#### Option 2: Application + Database + Redis Cache

Build and start the containers with both the base and cache configuration:

```bash
docker-compose -f docker-compose.yml -f docker-compose.cache.yml up --build -d
```

This will start the application with both PostgreSQL and Redis cache enabled.

> The backend service will be available at `http://localhost:8000/` in both deployment options.

---

## **Folder Structure**

```
├── apps
│   ├── __init__.py
│   ├── authors
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── books
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── common
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── reviews
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── sales
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations
│       │   ├── __init__.py
│       │   └── 0001_initial.py
│       ├── models.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── book_review_web
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── data_fixture.json
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── README.md
└── requirements.txt
```

---

## **Available Commands**

- Run migrations:

```bash
docker-compose exec backend python manage.py migrate
```

- Run seeds:

```bash
docker-compose exec backend python manage.py loaddata fixtures/*
```

- Connect to console:

```bash
docker exec -it nombre_del_contenedor python manage.py shell
```

- Create a superuser:

```bash
docker-compose exec backend python manage.py createsuperuser
```

- Run tests:

```bash
docker-compose exec backend python manage.py test
```

---

## **Environment Variables**

- `DATABASE_URL` is used by the backend to connect to PostgreSQL.
- Default database: `book_review`
- Default user: `postgres`
- Default password: `postgres`

---

## **Notes**

- Make sure Docker is installed and running.
