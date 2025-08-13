from django.db import models

from apps.books.models import Book


class Sale(models.Model):
	book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="yearly_sales")
	year = models.PositiveIntegerField()
	sales = models.PositiveIntegerField(default=0)

	class Meta:
		unique_together = ("book", "year")
		ordering = ["-year"]
		indexes = [
			models.Index(fields=["book", "year"]),
			models.Index(fields=["year"]),
		]

