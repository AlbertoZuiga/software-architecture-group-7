from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

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
        if year_val < 0 or year_val > 2025:
            errors["year"] = "Debe estar entre 0 y 2025"
    except (TypeError, ValueError):
        errors["year"] = "Año inválido"

    if not errors.get("year"):
        if Sale.objects.filter(book=book, year=year_val).exists():
            errors["year"] = "Ya existe una venta para este año en este libro"

    try:
        sales_val = int(sales_raw)
        if sales_val < 0:
            errors["sales"] = "Debe ser un número positivo"
    except (TypeError, ValueError):
        errors["sales"] = "Cantidad de ventas inválida"

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
            },
            status=400,
        )

    # Crear la venta
    Sale.objects.create(book=book, year=year_val, sales=sales_val)
    return redirect("sales:index", book_id=book.id)
