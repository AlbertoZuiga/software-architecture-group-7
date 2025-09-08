from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.reviews.models import Review, ReviewUpvote
from apps.common.utils import render_book_detail
from apps.common.search_service import search_service

from .models import Author, Book


def books_index(request):
    from django.core.cache import cache

    query = (request.GET.get("q") or "").strip()

    if query:
        # Use the search service which handles ElasticSearch or database search
        book_list = search_service.search_books(query, Book.objects.all())
    else:
        cache_key = "books_index:all"
        book_list = cache.get(cache_key)

        if book_list is None:
            book_list = Book.objects.all()

            cache.set(cache_key, book_list, 300)

    paginator = Paginator(book_list, 10)

    page_number = request.GET.get("page")
    books = paginator.get_page(page_number)

    cache_key = "authors:all"
    authors = cache.get(cache_key)
    if authors is None:
        authors = Author.objects.all()
        cache.set(cache_key, authors, 300)

    return render(
        request,
        "books/books_index.html",
        {
            "books": books,
            "q": query,
            "erorrs": {},
            "form_values": {},
            "authors": authors,
            "submit_label": "Create",
        },
    )


def books_show(request, book_id):
    from apps.common.cache_utils import get_from_cache_or_db
    from django.core.cache import cache

    def fetch_book():
        try:
            book = Book.objects.get(id=book_id)
            book.recompute_total_sales()
            return book
        except Book.DoesNotExist:
            return None

    book = get_from_cache_or_db("book", book_id, fetch_book)
    if not book:
        return redirect("books:index")


    reviews_cache_key = f"book_reviews:{book_id}"
    reviews = None

    if not request.user.is_authenticated:
        reviews = cache.get(reviews_cache_key)

    if reviews is None:
        reviews = Review.objects.filter(book=book).prefetch_related("reviewupvotes", "user")

        for review in reviews:
            review.recompute_up_votes_count()

        if not request.user.is_authenticated:
            cache.set(reviews_cache_key, reviews, 300)

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
        cover_image = request.FILES.get("cover_image")
        MAX_NAME_LENGTH = 255
        MAX_SUMMARY_LENGTH = 2000

        if len(name) > MAX_NAME_LENGTH:
            errors["name"] = f"Name cannot exceed {MAX_NAME_LENGTH} characters."
        if len(summary) > MAX_SUMMARY_LENGTH:
            errors["summary"] = f"Summary cannot exceed {MAX_SUMMARY_LENGTH} characters."

        published_at_str = request.POST.get("published_at", "").strip()
        author_id = request.POST.get("author", "").strip()

        form_values = {
            "name": name,
            "summary": summary,
            "published_at": published_at_str,
            "author": author_id,
        }

        try:
            published_at = timezone.datetime.strptime(
                published_at_str,
                "%Y-%m-%d"
            ).date() if published_at_str else None
        except ValueError:
            errors["published_at"] = "Formato de fecha inválido. Use YYYY-MM-DD."
            published_at = None

        author = Author.objects.get(id=author_id) if author_id else None

        if not name:
            errors["name"] = "Name is required."
        if not summary:
            errors["summary"] = "Summary is required."
        if not published_at:
            errors["published_at"] = "Publication date is required."
        if not author_id:
            errors["author"] = "Author is required."
        elif not author:
            errors["author"] = "Selected author does not exist."

        if published_at and author and author.date_of_birth:
            if published_at < author.date_of_birth:
                errors["published_at"] = (
                    "Publication date cannot be earlier "
                    "than the author's date of birth."
                )
            elif published_at > timezone.now().date():
                errors["published_at"] = "Publication date cannot be in the future."

        if not errors:
            book_data = {
                'name': name,
                'summary': summary,
                'published_at': published_at,
                'author_id': author_id
            }
            if cover_image:
                book_data['cover_image'] = cover_image
            
            Book.objects.create(**book_data)
            return redirect("books:index")

    authors = Author.objects.all()
    book_list = Book.objects.all()

    paginator = Paginator(book_list, 10)

    page_number = request.GET.get("page")
    books = paginator.get_page(page_number)

    return render(
        request,
        "books/books_index.html",
        {
            "errors": errors,
            "form_values": form_values,
            "authors": authors,
            "books": books,
            "submit_label": "Create"
        },
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
        cover_image = request.FILES.get("cover_image")

        form_values = {
            "name": name,
            "summary": summary,
            "published_at": published_at_str,
            "author": author_id,
        }

        try:
            published_at = timezone.datetime.strptime(
                published_at_str,
                "%Y-%m-%d"
            ).date() if published_at_str else None
        except ValueError:
            errors["published_at"] = "Invalid date format. Use YYYY-MM-DD."
            published_at = None

        if not name:
            errors["name"] = "Name is required."
        if not summary:
            errors["summary"] = "Summary is required."
        if not published_at:
            errors["published_at"] = "Publication date is required."
        if not author_id:
            errors["author"] = "Author is required."
        elif not Author.objects.filter(id=author_id).exists():
            errors["author"] = "Selected author does not exist."
        else:
            author = Author.objects.get(id=author_id)
            if published_at and author.date_of_birth:
                if published_at < author.date_of_birth:
                    errors["published_at"] = (
                    "Publication date cannot be earlier "
                    "than the author's date of birth."
                    )
                elif published_at > timezone.now().date():
                    errors["published_at"] = "Publication date cannot be in the future."

        if not errors:
            book.name = name
            book.summary = summary
            book.published_at = published_at
            book.author_id = author_id
            if cover_image:
                book.cover_image = cover_image
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
            "submit_label": "Update",
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
