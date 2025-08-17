from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.reviews.models import Review, ReviewUpvote
from apps.common.utils import render_book_detail

from .models import Author, Book


def books_index(request):
    query = (request.GET.get("q") or "").strip()
    book_list = Book.objects.all()

    if query:
        vector = SearchVector("summary", "name")
        search_query = SearchQuery(query)
        book_list = book_list.annotate(search=vector).filter(search=search_query)

    paginator = Paginator(book_list, 10)

    page_number = request.GET.get("page")
    books = paginator.get_page(page_number)

    authors = Author.objects.all()

    return render(
        request,
        "books/books_index.html",
        {
            "books": books,
            "q": query,
            "erorrs": {},
            "form_values": {},
            "authors": authors,
            "submit_label": "Crear",
        },
    )


def books_show(request, book_id):
    book = Book.objects.get(id=book_id)
    book.recompute_total_sales()

    reviews = Review.objects.filter(book=book).prefetch_related("reviewupvotes", "user")

    for review in reviews:
        review.recompute_up_votes_count()

    user_upvoted_review_ids = []
    if request.user.is_authenticated:
        user_upvoted_review_ids = list(
            ReviewUpvote.objects.filter(user=request.user, review__in=reviews).values_list(
                "review_id", flat=True
            )
        )

    sales = book.yearly_sales.all().order_by("-year")
    return render_book_detail(
        request,
        book,
        reviews,
        user_upvoted_review_ids=list(user_upvoted_review_ids),
        sales=sales,
    )


def books_create(request):
    errors = {}
    form_values = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        summary = request.POST.get("summary", "").strip()
        MAX_NAME_LENGTH = 255
        MAX_SUMMARY_LENGTH = 2000

        if len(name) > MAX_NAME_LENGTH:
            errors["name"] = f"El nombre no puede exceder {MAX_NAME_LENGTH} caracteres."
        if len(summary) > MAX_SUMMARY_LENGTH:
            errors["summary"] = f"El resumen no puede exceder {MAX_SUMMARY_LENGTH} caracteres."

        published_at_str = request.POST.get("published_at", "").strip()
        author_id = request.POST.get("author", "").strip()

        form_values = {
            "name": name,
            "summary": summary,
            "published_at": published_at_str,
            "author": author_id,
        }

        try:
            published_at = timezone.datetime.strptime(published_at_str, "%Y-%m-%d").date() if published_at_str else None
        except ValueError:
            errors["published_at"] = "Formato de fecha inválido. Use YYYY-MM-DD."
            published_at = None

        author = Author.objects.get(id=author_id) if author_id else None

        if not name:
            errors["name"] = "El nombre es obligatorio."
        if not summary:
            errors["summary"] = "El resumen es obligatorio."
        if not published_at:
            errors["published_at"] = "La fecha de publicación es obligatoria."
        if not author_id:
            errors["author"] = "El autor es obligatorio."
        elif not author:
            errors["author"] = "El autor seleccionado no existe."
        
        if published_at and author and author.date_of_birth:
            if published_at < author.date_of_birth:
                errors["published_at"] = "La fecha de publicación no puede ser anterior a la fecha de nacimiento del autor."
            elif published_at > timezone.now().date():
                errors["published_at"] = "La fecha de publicación no puede ser en el futuro."

        if not errors:
            Book.objects.create(
                name=name, summary=summary, published_at=published_at, author_id=author_id
            )
            return redirect("books:index")

    authors = Author.objects.all()
    book_list = Book.objects.all()

    paginator = Paginator(book_list, 10)

    page_number = request.GET.get("page")
    books = paginator.get_page(page_number)
    
    return render(
        request,
        "books/books_index.html",
        {"errors": errors, "form_values": form_values, "authors": authors, "books": books, "submit_label": "Crear"},
    )


def books_update(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    errors = {}
    form_values = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        summary = request.POST.get("summary", "").strip()
        published_at_str = request.POST.get("published_at", "").strip()
        author_id = request.POST.get("author", "").strip()

        form_values = {
            "name": name,
            "summary": summary,
            "published_at": published_at_str,
            "author": author_id,
        }

        try:
            published_at = timezone.datetime.strptime(published_at_str, "%Y-%m-%d").date() if published_at_str else None
        except ValueError:
            errors["published_at"] = "Formato de fecha inválido. Use YYYY-MM-DD."
            published_at = None

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
        else:
            author = Author.objects.get(id=author_id)
            if published_at and author.date_of_birth:
                if published_at < author.date_of_birth:
                    errors["published_at"] = "La fecha de publicación no puede ser anterior a la fecha de nacimiento del autor."
                elif published_at > timezone.now().date():
                    errors["published_at"] = "La fecha de publicación no puede ser en el futuro."

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
            "author": str(book.author_id),
        }

    authors = Author.objects.all()
    return render(
        request,
        "books/books_update.html",
        {
            "book": book,
            "errors": errors,
            "form_values": form_values,
            "authors": authors,
            "submit_label": "Actualizar",
        },
    )


@require_http_methods(["GET", "POST"])
def books_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("books:show", book_id=book.id)

    if request.method == "POST":
        book.delete()
        return redirect("books:index")

    return render(request, "books/books_confirm_delete.html", {"book": book})
