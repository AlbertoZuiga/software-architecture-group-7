# Book Review Platform

A modern, modular Django-based application for cataloging, reviewing, and tracking book sales, with support for both cached and non-cached deployments.

## Overview

This project is a book review platform built with Django, featuring a modular architecture with separate apps for authors, books, reviews, and sales data. The platform allows users to browse books, leave reviews, upvote existing reviews, and track book sales statistics. The application is fully containerized using Docker for easy deployment.

## Features

- **Author Management**: Create, view, and update author profiles
- **Book Catalog**: Browse and search books with detailed information
- **Review System**: Add book reviews with ratings and upvote functionality
- **Sales Tracking**: Record and display book sales statistics
- **Caching Support**: Optional Redis caching for improved performance
- **Responsive Design**: Mobile-friendly user interface

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- Git

## Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/AlbertoZuiga/software-architecture-group-7.git
cd software-architecture-group-7
```

2. Choose one of the deployment options:

### Deployment Options

#### Option 1: Application + Database

Build and start the application with PostgreSQL only:

```bash
docker-compose up --build -d
```

Only the main app and database are started.

#### Option 2: Application + Database + Redis Cache

Build and start the application with PostgreSQL and Redis caching:

```bash
docker-compose -f docker-compose.cache.yml up --build -d
```

This configuration activates Redis for caching frequently accessed data like author information, book details, and review scores. The cache stack runs on separate ports and can be isolated from the default stack.

#### Option 3: Application + Database + Reverse Proxy

Build and start the application with PostgreSQL and a reverse proxy:

```bash
docker-compose -f docker-compose.proxy.yml up --build -d
```

The application will be available at:

- [http://localhost:8000/](http://localhost:8000/)

---

### Initial Setup

After deployment, run the following commands to set up the database:

1. Apply migrations:

```bash
docker-compose exec backend python manage.py migrate
```

2. Load sample data (optional):

```bash
docker-compose exec backend python manage.py loaddata fixtures/*
```

3. Create an admin user:

```bash
docker-compose exec backend python manage.py createsuperuser
```

## Architecture

The project follows a modular Django architecture with separate apps for different functionalities:

### Key Components

- **apps/authors**: Author information and management
- **apps/books**: Book catalog and details
- **apps/reviews**: User reviews and rating system
- **apps/sales**: Book sales data and statistics
- **apps/common**: Shared functionality and utilities
- **book_review_web**: Core Django project settings and configuration

### Caching Implementation

The application supports optional Redis caching for improved performance:

- **Cache Keys**: Follow a standardized format (e.g., "author:1", "book:5", "review_score:42")
- **Cache Duration**: 5 minutes by default
- **Invalidation**: Automatic cache invalidation via Django signals when data changes

## Usage

### Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` to manage all data.

### Main Application

The main application is accessible at `http://localhost:8000/` with the following sections:

- **Authors**: Browse and manage author information
- **Books**: View the book catalog with filtering and search
- **Reviews**: Read and write book reviews
- **Statistics**: View sales statistics for books

## Development

### Project Structure

```
├── apps/                   # Django applications
│   ├── authors/            # Author management
│   ├── books/              # Book catalog
│   ├── common/             # Shared utilities
│   ├── reviews/            # Review system
│   └── sales/              # Sales tracking
├── book_review_web/        # Django project settings
├── fixtures/               # Sample data
├── static/                 # Static assets
├── docker-compose.yml      # Base deployment configuration
├── docker-compose.cache.yml # Redis cache configuration
├── Dockerfile              # Container definition
└── requirements.txt        # Python dependencies
```

### Common Commands

#### Docker Commands

- Start all services:

  ```bash
  docker-compose up -d
  ```

- Stop all services:

  ```bash
  docker-compose down
  ```

- View logs:
  ```bash
  docker-compose logs -f
  ```

#### Django Management Commands

- Run migrations:

  ```bash
  docker-compose exec backend python manage.py migrate
  ```

- Access Django shell:

  ```bash
  docker-compose exec backend python manage.py shell
  ```

- Run tests:
  ```bash
  docker-compose exec backend python manage.py test
  ```

## Environment Variables

The application uses the following environment variables:

| Variable       | Description               | Default                                            |
| -------------- | ------------------------- | -------------------------------------------------- |
| `DATABASE_URL` | PostgreSQL connection URL | `postgres://postgres:postgres@db:5432/book_review` |
| `USE_CACHE`    | Enable Redis caching      | `false` or `true` depending on deployment          |
| `REDIS_HOST`   | Redis server hostname     | `redis`                                            |
| `REDIS_PORT`   | Redis server port         | `6379`                                             |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).

## Troubleshooting

- **Connection Issues**: Ensure all containers are running with `docker-compose ps`
- **Database Errors**: Verify PostgreSQL container is healthy with `docker-compose logs db`
- **Cache Not Working**: Check Redis connection with `docker-compose exec redis redis-cli ping`
