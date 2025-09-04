from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Author

CURRENT_YEAR = datetime.now().year


def authors_index(request):
    from django.core.cache import cache
    
    # For index views, we use a simpler cache key without query params to avoid excessive cache entries
    cache_key = "authors_index:all"
    author_list = cache.get(cache_key)
    
    if author_list is None:
        author_list = Author.objects.all()
        cache.set(cache_key, author_list, 300)  # Cache for 5 minutes
    
    paginator = Paginator(author_list, 10)

    page_number = request.GET.get("page")
    authors = paginator.get_page(page_number)

    return render(request, "authors/authors_index.html", {"authors": authors})


def authors_show(request, author_id):
    from apps.common.cache_utils import get_from_cache_or_db

    def fetch_author():
        return (
            Author.objects
            .annotate(total_sales=Coalesce(Sum("books__yearly_sales__sales"), 0))
            .get(id=author_id)
        )

    author = get_from_cache_or_db("author", author_id, fetch_author)
    return render(request, "authors/authors_show.html", {"author": author})


def authors_create(request):
    errors = {}
    form_values = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        country = request.POST.get("country", "").strip()
        date_of_birth_raw = request.POST.get("date_of_birth", "").strip()
        description = request.POST.get("description", "").strip()
        photo = request.FILES.get("photo")

        form_values["name"] = name
        form_values["country"] = country
        form_values["date_of_birth"] = date_of_birth_raw
        form_values["description"] = description

        if not name:
            errors["name"] = "Name is required."
        if not country:
            errors["country"] = "Country is required."

        dob = None
        if date_of_birth_raw:
            try:
                dob = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
                if dob > datetime.now().date():
                    errors["date_of_birth"] = "Birth date cannot be in the future."
            except ValueError:
                errors["date_of_birth"] = "Invalid date format (YYYY-MM-DD)"

        if not errors:
            author_data = {
                'name': name,
                'country': country,
                'date_of_birth': dob,
                'description': description
            }
            if photo:
                author_data['photo'] = photo
                
            Author.objects.create(**author_data)
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
        photo = request.FILES.get("photo")

        form_values["name"] = name
        form_values["country"] = country
        form_values["date_of_birth"] = date_of_birth_raw
        form_values["description"] = description

        if not name:
            errors["name"] = "Name is required."
        if not country:
            errors["country"] = "Country is required."

        dob = None
        if date_of_birth_raw:
            try:
                dob = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
                if dob > datetime.now().date():
                    errors["date_of_birth"] = "Birth date cannot be in the future."
            except ValueError:
                errors["date_of_birth"] = "Invalid date format (YYYY-MM-DD)"

        if not errors:
            author.name = name
            author.country = country
            author.date_of_birth = dob
            author.description = description
            if photo:
                author.photo = photo
            author.save()
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
