from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.common.cache_utils import invalidate_cache
from apps.common.search_service import search_service
from .models import Book


@receiver(post_save, sender=Book)
def book_save_handler(sender, instance, **kwargs):
    # Invalidate individual book cache
    invalidate_cache("book", instance.id)
    
    # Invalidate book counts for authors
    invalidate_cache("method:books_count:Author", instance.author_id)
    
    # Invalidate book index page cache
    cache.delete("books_index:all")
    
    # Invalidate book reviews cache
    invalidate_cache("book_reviews", instance.id)
    
    # Sync with ElasticSearch
    search_service.index_book(instance)


@receiver(post_delete, sender=Book)
def book_delete_handler(sender, instance, **kwargs):
    # Invalidate individual book cache
    invalidate_cache("book", instance.id)
    
    # Invalidate book counts for authors
    invalidate_cache("method:books_count:Author", instance.author_id)
    
    # Invalidate book index page cache
    cache.delete("books_index:all")
    
    # Invalidate book reviews cache
    invalidate_cache("book_reviews", instance.id)
    
    # Remove from ElasticSearch
    search_service.delete_book(instance.id)
