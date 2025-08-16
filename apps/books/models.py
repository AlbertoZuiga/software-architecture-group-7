from django.db import models

from apps.authors.models import Author


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    name = models.CharField(max_length=255)
    summary = models.TextField(max_length=2000)
    published_at = models.DateField()

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
        self.total_sales = agg.get("total") or 0
        self.save(update_fields=["total_sales"])
