from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Book


def books_index(request):
    book_list = Book.objects.all()
    paginator = Paginator(book_list, 10)  # 10 libros por página

    page_number = request.GET.get("page")
    books = paginator.get_page(page_number)

    return render(request, "books/books_index.html", {"books": books})


def books_show(request, book_id):
    book = Book.objects.get(id=book_id)
    reviews = book.reviews.all().order_by("-up_votes", "-score")
    return render(request, "books/books_show.html", {"book": book, "reviews": reviews})
