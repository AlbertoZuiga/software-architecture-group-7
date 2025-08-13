from django.db import models

from apps.books.models import Book


class Review(models.Model):
	book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
	review = models.TextField()
	score = models.PositiveSmallIntegerField()
	up_votes = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ["-up_votes", "-score"]
		indexes = [
			models.Index(fields=["book", "score"]),
			models.Index(fields=["up_votes"]),
		]

	def __str__(self) -> str:  
		return f"{self.book.name}:{self.score}"


