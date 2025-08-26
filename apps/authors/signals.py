from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.common.cache_utils import invalidate_cache
from .models import Author


@receiver(post_save, sender=Author)
def author_save_handler(sender, instance, **kwargs):
    """
    Invalidate author cache when an author is saved or updated
    """
    # Invalidate individual author cache
    invalidate_cache("author", instance.id)
    
    # Invalidate authors index page cache
    cache.delete("authors_index:all")
    
    # Invalidate full authors list cache used in forms
    cache.delete("authors:all")
    
    # Books associated with this author might need to be refreshed
    cache.delete("books_index:all")


@receiver(post_delete, sender=Author)
def author_delete_handler(sender, instance, **kwargs):
    """
    Invalidate author cache when an author is deleted
    """
    # Invalidate individual author cache
    invalidate_cache("author", instance.id)
    
    # Invalidate authors index page cache
    cache.delete("authors_index:all")
    
    # Invalidate full authors list cache used in forms
    cache.delete("authors:all")
    
    # Books associated with this author might need to be refreshed
    cache.delete("books_index:all")
