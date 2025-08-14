from django.core.paginator import Paginator
from django.shortcuts import render

from apps.books.models import Book
from .models import Sale


def sales_index(request, book_id):
    book = Book.objects.get(id=book_id)
    book.recompute_total_sales()
    sale_list = Sale.objects.filter(book_id=book_id)
    paginator = Paginator(sale_list, 10)

    page_number = request.GET.get("page")
    sales = paginator.get_page(page_number)

    return render(request, "sales/sales_index.html", {"book": book, "sales": sales})
