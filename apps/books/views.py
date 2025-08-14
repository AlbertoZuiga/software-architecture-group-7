from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery

import re

from .models import Book


def books_index(request):
    query = (request.GET.get("q") or "").strip()
    book_list = Book.objects.all()

    if query:
        vector = SearchVector('summary', 'name')
        search_query = SearchQuery(query)
        book_list = book_list.annotate(search=vector).filter(search=search_query)

    paginator = Paginator(book_list, 10)  

    page_number = request.GET.get("page")
    books = paginator.get_page(page_number)

    return render(request, "books/books_index.html", {"books": books, "q": query})


def books_show(request, book_id):
    book = Book.objects.get(id=book_id)
    reviews = book.reviews.all().order_by("-up_votes", "-score")
    return render(request, "books/books_show.html", {"book": book, "reviews": reviews})
