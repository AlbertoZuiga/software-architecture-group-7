from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def books_count(self) -> int:
        return self.books.count()
