from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from .models import Author


def authors_index(request):
    author_list = Author.objects.all()
    paginator = Paginator(author_list, 10)  # 10 libros por página

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

        form_values["name"] = name
        form_values["country"] = country

        if not name:
            errors["name"] = "El nombre es obligatorio."
        if not country:
            errors["country"] = "El país es obligatorio."

        if not errors:
            Author.objects.create(name=name, country=country)
            return redirect("authors:index")

    return render(request, "authors/authors_create.html", {
        "errors": errors,
        "form_values": form_values
    })

def authors_update(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    errors = {}
    form_values = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        country = request.POST.get("country", "").strip()

        form_values["name"] = name
        form_values["country"] = country

        if not name:
            errors["name"] = "El nombre es obligatorio."
        if not country:
            errors["country"] = "El país es obligatorio."

        if not errors:
            author.name = name
            author.country = country
            author.save()
            return redirect("authors:index")

    return render(request, "authors/authors_update.html", {
        "author": author,
        "errors": errors,
        "form_values": form_values
    })
