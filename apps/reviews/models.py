from django.contrib.auth.models import User
from django.db import IntegrityError, models

from apps.books.models import Book


from apps.common.cache_utils import cached_method, get_cache_key, invalidate_cache, cache

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
            invalidate_cache("review_score", self.id)
            return True
        except IntegrityError:
            return False

    def remove_upvote(self, user):
        try:
            upvote = ReviewUpvote.objects.get(review=self, user=user)
            upvote.delete()
            invalidate_cache("review_score", self.id)
            return True
        except ReviewUpvote.DoesNotExist:
            return False

    def recompute_up_votes_count(self):
        # Get from cache or compute
        cache_key = get_cache_key("review_score", self.id)
        cached_count = cache.get(cache_key)

        if cached_count is None:
            count = self.reviewupvotes.count()
            cache.set(cache_key, count, 300)  # Cache for 5 minutes
            self.up_votes = count
        else:
            self.up_votes = cached_count

        self.save(update_fields=["up_votes"])


class ReviewUpvote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reviewupvotes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="upvoted_reviews")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")
