from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='authors/', null=True, blank=True, help_text="Foto del autor")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def books_count(self) -> int:
        """
        Count the number of books by this author
        Using simple property instead of cached_method as properties don't work well with method decorators
        """
        return self.books.count()
