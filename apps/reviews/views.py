from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpRequest, HttpResponse

from apps.books.models import Book
from .models import Review


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
		reviews = book.reviews.all().order_by('-up_votes', '-score')
		return render(
			request,
			'books/books_show.html',
			{
				'book': book,
				'reviews': reviews,
				'errors': errors,
				'form_values': {'review': review_text, 'score': score_raw or ''},
			},
			status=400,
		)

	Review.objects.create(book=book, review=review_text, score=score_val)
	return redirect("books:show", book_id=book.id)
