from django.db.models import Avg, Count, Sum
from django.shortcuts import render

from apps.authors.models import Author
from apps.books.models import Book
from apps.sales.models import Sale


def stats_page(request):
    top_rated_books_qs = (
        Book.objects
        .annotate(average_score=Avg("reviews__score"))
        .order_by("-average_score")[:10]
    )

    top_rated_books = list(
        top_rated_books_qs.prefetch_related("reviews")
    )
    for book in top_rated_books:
        reviews = list(book.reviews.all())
        if reviews:
            best = max(reviews, key=lambda r: (r.score, r.up_votes))
            worst = min(reviews, key=lambda r: (r.score, -r.up_votes))
            book.best_review_upvotes = best.review
            book.worst_review_upvotes = worst.review
        else:
            book.best_review_upvotes = "N/A"
            book.worst_review_upvotes = "N/A"


    authors_stats = (
        Author.objects
        .annotate(
            number_of_books=Count("books", distinct=True),
            average_score=Avg("books__reviews__score"),
            total_sales=Sum("books__yearly_sales__sales"),
        )
    )

    top_selling_books_qs = (
        Book.objects
        .annotate(
            calculated_total_sales=Sum("yearly_sales__sales"),
            author_total_sales=Sum("author__books__yearly_sales__sales"),
        )
        .order_by("-calculated_total_sales")[:50]
        .select_related("author")
    )
    top_selling_books = list(top_selling_books_qs)

    publication_years = set()
    book_ids = []
    for b in top_selling_books:
        if b.published_at:
            publication_years.add(b.published_at.year)
        book_ids.append(b.id)

    if publication_years:
        sales_qs = (
            Sale.objects
            .filter(year__in=publication_years)
            .values("year", "book_id", "sales")
            .order_by("year", "-sales", "book_id")
        )
        top5_book_ids = set()
        current_year = None
        count_in_year = 0
        for row in sales_qs:
            y = row["year"]
            if y != current_year:
                current_year = y
                count_in_year = 0
            if count_in_year < 5:
                top5_book_ids.add(row["book_id"])
                count_in_year += 1
    else:
        top5_book_ids = set()

    for b in top_selling_books:
        pub_year = b.published_at.year if b.published_at else None
        b.is_top_5_in_year = (b.id in top5_book_ids) if pub_year else False

    context = {
        "top_rated_books": top_rated_books,
        "authors_stats": authors_stats,
        "top_selling_books": top_selling_books
    }
    return render(request, "stats/stats_index.html", context)