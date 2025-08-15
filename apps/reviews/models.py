from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError

from apps.books.models import Book

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    review = models.TextField()
    score = models.PositiveSmallIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    up_votes = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ["-score"]
        indexes = [
            models.Index(fields=["book", "score"]),
        ]

    def __str__(self) -> str:
        return f"{self.book.name}:{self.score}"

    def add_upvote(self, user):
        try:
            ReviewUpvote.objects.create(review=self, user=user)
            return True
        except IntegrityError:
            return False

    def recompute_up_votes_count(self):
        self.up_votes = self.reviewupvotes.count()
        self.save()

class ReviewUpvote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reviewupvotes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="upvoted_reviews")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')
