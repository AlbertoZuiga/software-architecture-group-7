# Software Architecture Group 7

This project is a **Django-based book review platform** with modular apps for authors, books, reviews, and sales. It is fully containerized using Docker for easy setup.

---

## **Getting Started**

Clone the repository and navigate into the project folder:

```bash
git clone https://github.com/AlbertoZuiga/software-architecture-group-7.git
cd software-architecture-group-7
```

Build and start the containers using Docker Compose:

```bash
docker-compose up --build -d
```

> The backend service will be available at `http://localhost:8000/`.

---

## **Folder Structure**

```
├── apps
│   ├── authors      # Handles author-related data and views
│   ├── books        # Handles book-related data and views
│   ├── common       # Shared models and utilities
│   ├── reviews      # Handles book reviews
│   └── sales        # Handles sales data and functionality
├── book_review_web  # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── docker-compose.yml
├── Dockerfile
├── manage.py
└── README.md
```

---

## **Available Commands**

* Run migrations:

```bash
docker-compose exec backend python manage.py migrate
```

* Create a superuser:

```bash
docker-compose exec backend python manage.py createsuperuser
```

* Run tests:

```bash
docker-compose exec backend python manage.py test
```

---

## **Environment Variables**

* `DATABASE_URL` is used by the backend to connect to PostgreSQL.
* Default database: `book_review`
* Default user: `postgres`
* Default password: `postgres`

---

## **Notes**

* Make sure Docker is installed and running.
