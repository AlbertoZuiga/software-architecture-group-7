from django.db.models import Avg, Count, Sum
from django.shortcuts import render

from apps.authors.models import Author
from apps.books.models import Book


def stats_page(request):
    top_rated_books = Book.objects.annotate(
        average_score=Avg("reviews__score")
    ).order_by("-average_score")[:10]

    for book in top_rated_books:
        best_review = book.reviews.order_by("-score", "-up_votes").first()
        worst_review = book.reviews.order_by("score", "-up_votes").first()
        book.best_review_upvotes = best_review.review if best_review else "N/A"
        book.worst_review_upvotes = worst_review.review if worst_review else "N/A"

    sort_field = request.GET.get("sort", "total_sales")
    sort_direction = request.GET.get("direction", "desc")
    sort_order = f"-{sort_field}" if sort_direction == "desc" else sort_field

    authors_stats = Author.objects.annotate(
        number_of_books=Count("books"),
        average_score=Avg("books__reviews__score"),
        total_sales=Sum("books__yearly_sales__sales"),
    ).order_by(sort_order)

    top_selling_books = Book.objects.annotate(
        calculated_total_sales=Sum("yearly_sales__sales"),
        author_total_sales=Sum("author__books__yearly_sales__sales"),
    ).order_by("-calculated_total_sales")[:50]

    for book in top_selling_books:
        yearly_sales = book.yearly_sales.all()
        top_5_sales = yearly_sales.order_by("-sales")[:5]
        book.is_top_5_in_year = any(sale.book_id == book.id for sale in top_5_sales)

    context = {
        "top_rated_books": top_rated_books,
        "authors_stats": authors_stats,
        "top_selling_books": top_selling_books,
        "current_sort_field": sort_field,
        "current_sort_direction": sort_direction,
    }
    return render(request, "stats/stats_index.html", context)
