from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.books.models import Book

from .models import Review


@login_required
@require_POST
def create_review(request: HttpRequest, book_id: int) -> HttpResponse:
    book = get_object_or_404(Book, id=book_id)
    review_text = (request.POST.get("review") or "").strip()
    score_raw = request.POST.get("score")
    errors = {}
    if not review_text:
        errors["review"] = "El texto es requerido"
    try:
        score_val = int(score_raw)
        if score_val < 1 or score_val > 5:
            errors["score"] = "Debe estar entre 1 y 5"
    except (TypeError, ValueError):
        errors["score"] = "Puntaje inválido"

    if errors:
        reviews = book.reviews.all().order_by("-up_votes", "-score")
        return render(
            request,
            "books/books_show.html",
            {
                "book": book,
                "reviews": reviews,
                "errors": errors,
                "form_values": {"review": review_text, "score": score_raw or ""},
            },
            status=400,
        )

    Review.objects.create(book=book, review=review_text, score=score_val, user=request.user)
    return redirect("books:show", book_id=book.id)


@login_required
@require_POST
def upvote_review(request: HttpRequest, review_id: int) -> HttpResponse:
    review = get_object_or_404(Review, id=review_id)
    success = review.add_upvote(user=request.user)
    if success:
        review.recompute_up_votes_count()

    return redirect("books:show", book_id=review.book_id)


@login_required
@require_POST
def delete_upvote_review(request: HttpRequest, review_id: int) -> HttpResponse:
    review = get_object_or_404(Review, id=review_id)
    success = review.remove_upvote(user=request.user)
    if success:
        review.recompute_up_votes_count()

    return redirect("books:show", book_id=review.book_id)


@login_required
def edit_review(request: HttpRequest, review_id: int) -> HttpResponse:
    review = get_object_or_404(Review, id=review_id)
    if not (request.user.is_superuser or review.user_id == request.user.id):
        return redirect("books:show", book_id=review.book_id)
    if request.method == "POST":
        text = (request.POST.get("review") or "").strip()
        score_raw = request.POST.get("score")
        errors = {}
        if not text:
            errors["review"] = "El texto es requerido"
        try:
            score_val = int(score_raw)
            if score_val < 1 or score_val > 5:
                errors["score"] = "Debe estar entre 1 y 5"
        except (TypeError, ValueError):
            errors["score"] = "Puntaje inválido"
        if not errors:
            review.review = text
            review.score = score_val
            review.save(update_fields=["review", "score"])
            return redirect("books:show", book_id=review.book_id)
        book = review.book
        reviews = book.reviews.all()
        return render(
            request,
            "books/books_show.html",
            {
                "book": book,
                "reviews": reviews,
                "edit_review_id": review.id,
                "errors": errors,
                "form_values": {"review": text, "score": score_raw or ""},
            },
            status=400,
        )
    # GET: show inline edit form within book page
    book = review.book
    reviews = book.reviews.all()
    return render(
        request,
        "books/books_show.html",
        {
            "book": book,
            "reviews": reviews,
            "edit_review_id": review.id,
            "form_values": {"review": review.review, "score": review.score},
        },
    )


@login_required
@require_POST
def delete_review(request: HttpRequest, review_id: int) -> HttpResponse:
    review = get_object_or_404(Review, id=review_id)
    if request.user.is_superuser or review.user_id == request.user.id:
        book_id = review.book_id
        review.delete()
        return redirect("books:show", book_id=book_id)
    return redirect("books:show", book_id=review.book_id)
