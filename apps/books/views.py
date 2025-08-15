from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.postgres.search import SearchVector, SearchQuery

from apps.reviews.models import Review, ReviewUpvote
from .models import Book, Author

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

    authors = Author.objects.all()

    return render(request, "books/books_index.html", {
        "books": books,
        "q": query,
        "erorrs": {},
        "form_values": {},
        "authors": authors,
        "submit_label": "Crear"
    })

def books_show(request, book_id):
    book = Book.objects.get(id=book_id)
    book.recompute_total_sales()

    reviews = Review.objects.filter(book=book).prefetch_related('reviewupvotes', 'user')
    
    # Recompute votes count for all reviews
    for review in reviews:
        review.recompute_up_votes_count()

    # Get the IDs of reviews that the current user has upvoted
    user_upvoted_review_ids = []
    if request.user.is_authenticated:
        user_upvoted_review_ids = list(
            ReviewUpvote.objects.filter(
                user=request.user,
                review__in=reviews
            ).values_list('review_id', flat=True)
        )

    sales = book.yearly_sales.all().order_by("-year")
    return render(
        request,
        "books/books_show.html",
        {
            "book": book,
            "reviews": reviews,
            "user_upvoted_review_ids": list(user_upvoted_review_ids),
            "sales": sales,
        }
    )

def books_create(request):
    errors = {}
    form_values = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        summary = request.POST.get("summary", "").strip()
        published_at = request.POST.get("published_at", "").strip()
        author_id = request.POST.get("author", "").strip()

        form_values = {
            "name": name,
            "summary": summary,
            "published_at": published_at,
            "author": author_id
        }

        if not name:
            errors["name"] = "El nombre es obligatorio."
        if not summary:
            errors["summary"] = "El resumen es obligatorio."
        if not published_at:
            errors["published_at"] = "La fecha de publicación es obligatoria."
        if not author_id:
            errors["author"] = "El autor es obligatorio."
        elif not Author.objects.filter(id=author_id).exists():
            errors["author"] = "El autor seleccionado no existe."

        if not errors:
            Book.objects.create(
                name=name,
                summary=summary,
                published_at=published_at,
                author_id=author_id
            )
            return redirect("books:index")

    authors = Author.objects.all()
    return render(request, "books/books_index.html", {
        "errors": errors,
        "form_values": form_values,
        "authors": authors,
        "submit_label": "Crear"
    })


def books_update(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    errors = {}
    form_values = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        summary = request.POST.get("summary", "").strip()
        published_at = request.POST.get("published_at", "").strip()
        author_id = request.POST.get("author", "").strip()

        form_values = {
            "name": name,
            "summary": summary,
            "published_at": published_at,
            "author": author_id
        }

        if not name:
            errors["name"] = "El nombre es obligatorio."
        if not summary:
            errors["summary"] = "El resumen es obligatorio."
        if not published_at:
            errors["published_at"] = "La fecha de publicación es obligatoria."
        if not author_id:
            errors["author"] = "El autor es obligatorio."
        elif not Author.objects.filter(id=author_id).exists():
            errors["author"] = "El autor seleccionado no existe."

        if not errors:
            book.name = name
            book.summary = summary
            book.published_at = published_at
            book.author_id = author_id
            book.save()
            return redirect("books:index")
    else:
        form_values = {
            "name": book.name,
            "summary": book.summary,
            "published_at": book.published_at,
            "author": str(book.author_id)
        }

    authors = Author.objects.all()
    return render(request, "books/books_update.html", {
        "book": book,
        "errors": errors,
        "form_values": form_values,
        "authors": authors,
        "submit_label": "Actualizar"
    })
