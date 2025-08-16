from django.shortcuts import render

from django.shortcuts import render
from django.db.models import Avg, Count, Sum, Case, When, BooleanField
from apps.authors.models import Author
from apps.books.models import Book
from apps.reviews.models import Review


def stats_page(request):
    # Table 2: Top 10 rated books with highest and lowest rated reviews
    top_rated_books = Book.objects.annotate(
        average_score=Avg('reviews__score')  # Use 'reviews__score' based on the related name
    ).order_by('-average_score')[:10]

    # Table 1: Authors with number of books, average score, and total sales
    sort_field = request.GET.get('sort', 'total_sales')  # Default sort by total_sales
    sort_direction = request.GET.get('direction', 'desc')  # Default sort direction is descending
    sort_order = f"-{sort_field}" if sort_direction == 'desc' else sort_field

    authors_stats = Author.objects.annotate(
        number_of_books=Count('books'),  # Use 'books' based on the related name
        average_score=Avg('books__reviews__score'),  # Use 'books__reviews__score'
        total_sales=Sum('books__yearly_sales__sales')  # Use 'books__yearly_sales__sales'
    ).order_by(sort_order)

    # Table 3: Top 50 selling books of all time
    top_selling_books = Book.objects.annotate(
        calculated_total_sales=Sum('yearly_sales__sales'),  # Total sales for the book
        author_total_sales=Sum('author__books__yearly_sales__sales')  # Total sales for the author
    ).order_by('-calculated_total_sales')[:50]

    # Add logic to determine if the book was in the top 5 selling books in its publication year
    for book in top_selling_books:
        yearly_sales = book.yearly_sales.all()  # Assuming a related name of 'yearly_sales'
        top_5_sales = yearly_sales.order_by('-sales')[:5]
        book.is_top_5_in_year = any(sale.book_id == book.id for sale in top_5_sales)

    # Pass the data to the template
    context = {
        'top_rated_books': top_rated_books,
        'authors_stats': authors_stats,
        'top_selling_books': top_selling_books,
        'current_sort_field': sort_field,
        'current_sort_direction': sort_direction,
    }
    return render(request, 'stats/stats_index.html', context)