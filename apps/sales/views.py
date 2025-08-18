from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.books.models import Book

from .models import Sale

CURRENT_YEAR = datetime.now().year
MAX_SALES = 2147483647


def sales_index(request, book_id):
    book = Book.objects.get(id=book_id)
    book.recompute_total_sales()
    sale_list = Sale.objects.filter(book_id=book_id)
    paginator = Paginator(sale_list, 10)

    page_number = request.GET.get("page")
    sales = paginator.get_page(page_number)

    return render(
        request,
        "sales/sales_index.html",
        {"book": book, "sales": sales, "current_year": CURRENT_YEAR},
    )


@login_required
@require_POST
def sales_create(request: HttpRequest, book_id: int) -> HttpResponse:
    book = get_object_or_404(Book, id=book_id)

    year_raw = request.POST.get("year")
    sales_raw = request.POST.get("sales")
    errors = {}
    form_values = {"year": year_raw or "", "sales": sales_raw or ""}

    try:
        year_val = int(year_raw)
        if year_val < book.published_at.year or year_val > CURRENT_YEAR:
            errors["year"] = "Must be between publication year and current year"
    except (TypeError, ValueError):
        errors["year"] = "Invalid year"

    if not errors.get("year"):
        if Sale.objects.filter(book=book, year=year_val).exists():
            errors["year"] = "A sale already exists for this year in this book"

    try:
        sales_val = int(sales_raw)
        if sales_val < 0:
            errors["sales"] = "Must be a positive number"
        elif sales_val > MAX_SALES:
            errors["sales"] = f"Cannot exceed {MAX_SALES} sales"
    except (TypeError, ValueError):
        errors["sales"] = "Invalid sales amount"

    if errors:
        sale_list = Sale.objects.filter(book=book).order_by("-id")
        paginator = Paginator(sale_list, 10)
        page_number = request.GET.get("page")
        sales = paginator.get_page(page_number)

        return render(
            request,
            "sales/sales_index.html",
            {
                "book": book,
                "sales": sales,
                "errors": errors,
                "form_values": form_values,
                "current_year": CURRENT_YEAR,
            },
            status=400,
        )

    Sale.objects.create(book=book, year=year_val, sales=sales_val)
    return redirect("sales:index", book_id=book.id)


@login_required
def sales_update(request: HttpRequest, book_id: int, sale_id: int) -> HttpResponse:
    book = get_object_or_404(Book, id=book_id)
    sale = get_object_or_404(Sale, id=sale_id, book=book)

    if request.method == "POST":
        year_raw = request.POST.get("year")
        sales_raw = request.POST.get("sales")
        errors = {}
        form_values = {"year": year_raw or "", "sales": sales_raw or ""}

        try:
            year_val = int(year_raw)
            if year_val < book.published_at.year or year_val > CURRENT_YEAR:
                errors["year"] = f"Must be between {book.published_at.year} and {CURRENT_YEAR}"
        except (TypeError, ValueError):
            errors["year"] = "Invalid year"

        if not errors.get("year"):
            if year_val != sale.year and Sale.objects.filter(book=book, year=year_val).exists():
                errors["year"] = "A sale already exists for this year in this book"

        try:
            sales_val = int(sales_raw)
            if sales_val < 0:
                errors["sales"] = "Must be a positive number"
            elif sales_val > MAX_SALES:
                errors["sales"] = f"Cannot exceed {MAX_SALES} sales"
        except (TypeError, ValueError):
            errors["sales"] = "Invalid sales amount"

        if errors:
            return render(
                request,
                "sales/sales_update.html",
                {
                    "book": book,
                    "sale": sale,
                    "errors": errors,
                    "form_values": form_values,
                    "current_year": CURRENT_YEAR,
                },
                status=400,
            )

        sale.year = year_val
        sale.sales = sales_val
        sale.save()
        return redirect("sales:index", book_id=book.id)

    # GET request: show edit form
    return render(
        request,
        "sales/sales_update.html",
        {
            "book": book,
            "sale": sale,
            "current_year": CURRENT_YEAR,
        },
    )


@login_required
@require_POST
def sales_delete(_request: HttpRequest, book_id: int, sale_id: int) -> HttpResponse:
    book = get_object_or_404(Book, id=book_id)
    sale = get_object_or_404(Sale, id=sale_id, book=book)
    sale.delete()
    return redirect("sales:index", book_id=book.id)
