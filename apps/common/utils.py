"""Utility functions for the application."""
from django.shortcuts import render

def render_book_detail(request, book, reviews, **extra_context):
    """
    Helper function to render book detail page with reviews.
    Args:
        request: The HTTP request
        book: The Book instance
        reviews: QuerySet of reviews
        **extra_context: Additional context to pass to the template
    Returns:
        Rendered response with the book detail template
    """
    context = {
        "book": book,
        "reviews": reviews,
    }
    context.update(extra_context)
    return render(
        request,
        "books/books_show.html",
        context,
    )
