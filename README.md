# Book Review Platform

A modern, modular Django-based application for cataloging, reviewing, and tracking book sales, with support for both cached and non-cached deployments.

## Overview

This project is a book review platform built with Django, featuring a modular architecture with separate apps for authors, books, reviews, and sales data. The platform allows users to browse books, leave reviews, upvote existing reviews, and track book sales statistics. The application is fully containerized using Docker for easy deployment.

## Features

- **Author Management**: Create, view, and update author profiles
- **Book Catalog**: Browse and search books with detailed information
- **Enhanced Search**: ElasticSearch integration for fast, fuzzy text search (optional)
- **Review System**: Add book reviews with ratings and upvote functionality
- **Sales Tracking**: Record and display book sales statistics
- **Caching Support**: Optional Redis caching for improved performance
- **Reverse Proxy**: Optional Nginx configuration for better performance and custom domains
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

#### Option 1: Application + Database (Default)

Build and start the application with PostgreSQL only:

```bash
docker-compose up --build -d
```

Only the main app and database are started. The application will be available at [http://localhost:8000/](http://localhost:8000/).

#### Option 2: Application + Database + Redis Cache

Build and start the application with PostgreSQL and Redis caching:

```bash
docker-compose -f docker-compose.cache.yml up --build -d
```

This configuration activates Redis for caching frequently accessed data like author information, book details, and review scores. The application will be available at [http://localhost:8000/](http://localhost:8000/).

#### Option 3: Application + Database + ElasticSearch

Build and start the application with PostgreSQL and ElasticSearch for enhanced search:

```bash
docker-compose -f docker-compose.elasticsearch.yml up --build -d
```

This configuration adds ElasticSearch for improved text search functionality. The application will be available at [http://localhost:8000/](http://localhost:8000/).

#### Option 4: Application + Database + Reverse Proxy

Build and start the application with PostgreSQL and Nginx reverse proxy:

```bash
docker-compose -f docker-compose.proxy.yml up --build -d
```

This configuration adds Nginx as a reverse proxy for better static file handling and request management. The application will be available at:

- [http://localhost](http://localhost)
- **Custom domain**: [app.localhost](app.localhost) (requires hosts file modification)

To use the custom domain, add the following line to your system's hosts file:
- **Windows**: `C:\Windows\System32\drivers\etc\hosts`
- **Linux/Mac**: `/etc/hosts`

```
127.0.0.1 app.localhost
```

#### Option 5: Full Setup (Application + Database + Cache + Search + Proxy)

Build and start the complete application with all components:

```bash
docker-compose -f docker-compose.full.yml up --build -d
```

This configuration includes PostgreSQL, Redis cache, ElasticSearch, and Nginx reverse proxy for maximum performance. The application will be available at:

- [http://localhost](http://localhost)
- **Custom domain**: [http://app.localhost/](http://app.localhost/) (requires hosts file modification)

To use the custom domain, add the following line to your system's hosts file:
- **Windows**: `C:\Windows\System32\drivers\etc\hosts`
- **Linux/Mac**: `/etc/hosts`

```
127.0.0.1 app.localhost
```

---



### Login Credentials

You can access the application with the following credentials:

- **Username**: `admin`
- **Password**: `admin1234`

These credentials provide full administrative access to the application.

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

### Main Application

The main application is accessible at `http://localhost:8000/` with the following sections:

- **Authors**: Browse and manage author information
- **Books**: View the book catalog with filtering and search
- **Reviews**: Read and write book reviews
- **Statistics**: View sales statistics for books




