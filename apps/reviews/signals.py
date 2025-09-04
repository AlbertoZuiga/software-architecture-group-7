from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.common.cache_utils import invalidate_cache
from .models import Review, ReviewUpvote


@receiver(post_save, sender=Review)
def review_save_handler(sender, instance, **kwargs):
    """
    Invalidate review cache when a review is saved or updated
    """
    # Invalidate individual review cache
    invalidate_cache("review", instance.id)
    invalidate_cache("review_score", instance.id)
    
    # Invalidate book reviews cache
    invalidate_cache("book_reviews", instance.book_id)
    cache.delete(f"book_reviews:{instance.book_id}")
    
    # The book's score/ratings might have changed
    invalidate_cache("book", instance.book_id)


@receiver(post_delete, sender=Review)
def review_delete_handler(sender, instance, **kwargs):
    """
    Invalidate review cache when a review is deleted
    """
    # Invalidate individual review cache
    invalidate_cache("review", instance.id)
    invalidate_cache("review_score", instance.id)
    
    # Invalidate book reviews cache
    invalidate_cache("book_reviews", instance.book_id)
    cache.delete(f"book_reviews:{instance.book_id}")
    
    # The book's score/ratings might have changed
    invalidate_cache("book", instance.book_id)


@receiver(post_save, sender=ReviewUpvote)
@receiver(post_delete, sender=ReviewUpvote)
def review_upvote_handler(sender, instance, **kwargs):
    """
    Invalidate review score cache when upvotes change
    """
    # Get the review object
    review = instance.review
    
    # Invalidate review score cache
    invalidate_cache("review_score", review.id)
    
    # Invalidate book reviews cache as review scores changed
    invalidate_cache("book_reviews", review.book_id)
    cache.delete(f"book_reviews:{review.book_id}")
