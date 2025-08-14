from django.core.paginator import Paginator
from django.shortcuts import render

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
