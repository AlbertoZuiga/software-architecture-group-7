from datetime import datetime

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Author

CURRENT_YEAR = datetime.now().year


def authors_index(request):
    author_list = Author.objects.all()
    paginator = Paginator(author_list, 10)

    page_number = request.GET.get("page")
    authors = paginator.get_page(page_number)

    return render(request, "authors/authors_index.html", {"authors": authors})


def authors_show(request, author_id):
    author = Author.objects.get(id=author_id)
    return render(request, "authors/authors_show.html", {"author": author})


def authors_create(request):
    errors = {}
    form_values = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        country = request.POST.get("country", "").strip()
        date_of_birth_raw = request.POST.get("date_of_birth", "").strip()
        description = request.POST.get("description", "").strip()

        form_values["name"] = name
        form_values["country"] = country
        form_values["date_of_birth"] = date_of_birth_raw
        form_values["description"] = description

        if not name:
            errors["name"] = "El nombre es obligatorio."
        if not country:
            errors["country"] = "El país es obligatorio."

        dob = None
        if date_of_birth_raw:
            try:
                dob = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
                if dob > datetime.now().date():
                    errors["date_of_birth"] = "La fecha de nacimiento no puede ser futura."
            except ValueError:
                errors["date_of_birth"] = "Fecha inválida (YYYY-MM-DD)"

        if not errors:
            Author.objects.create(
                name=name, country=country, date_of_birth=dob, description=description
            )
            return redirect("authors:index")

    author_list = Author.objects.all()
    paginator = Paginator(author_list, 10)

    page_number = request.GET.get("page")
    authors = paginator.get_page(page_number)

    return render(
        request,
        "authors/authors_index.html",
        {"authors": authors, "errors": errors, "form_values": form_values},
    )


def authors_update(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    errors = {}
    form_values = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        country = request.POST.get("country", "").strip()
        date_of_birth_raw = request.POST.get("date_of_birth", "").strip()
        description = request.POST.get("description", "").strip()

        form_values["name"] = name
        form_values["country"] = country
        form_values["date_of_birth"] = date_of_birth_raw
        form_values["description"] = description

        if not name:
            errors["name"] = "El nombre es obligatorio."
        if not country:
            errors["country"] = "El país es obligatorio."

        dob = None
        if date_of_birth_raw:
            try:
                dob = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
                if dob > datetime.now().date():
                    errors["date_of_birth"] = "La fecha de nacimiento no puede ser futura."
            except ValueError:
                errors["date_of_birth"] = "Fecha inválida (YYYY-MM-DD)"

        if not errors:
            author.name = name
            author.country = country
            author.date_of_birth = dob
            author.description = description
            author.save(update_fields=["name", "country", "date_of_birth", "description"])
            return redirect("authors:index")

    return render(
        request,
        "authors/authors_update.html",
        {"author": author, "errors": errors, "form_values": form_values},
    )


@require_POST
def authors_delete(_request, author_id):
    author = get_object_or_404(Author, id=author_id)
    author.delete()
    return redirect("authors:index")
