from django.db import models

from apps.authors.models import Author


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    name = models.CharField(max_length=255)
    summary = models.TextField(max_length=2000)
    published_at = models.DateField()
    cover_image = models.ImageField(upload_to='books/', null=True, blank=True, help_text="Imagen de portada del libro")

    total_sales = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["author"]),
        ]

    def __str__(self) -> str:
        return self.name

    def recompute_total_sales(self):
        agg = self.yearly_sales.aggregate(total=models.Sum("sales"))
        total = agg.get("total") or 0

        MAX_POSITIVE_INT = 2147483647
        total = min(total, MAX_POSITIVE_INT)

        self.total_sales = total
        self.save(update_fields=["total_sales"])
