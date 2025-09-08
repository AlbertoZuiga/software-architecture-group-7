from django.core.management.base import BaseCommand
from apps.common.search_service import search_service
from apps.books.models import Book


class Command(BaseCommand):
    help = 'Initialize ElasticSearch index and sync existing books'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reindex even if ElasticSearch is not available',
        )

    def handle(self, *args, **options):
        if not search_service.es_available and not options['force']:
            self.stdout.write(
                self.style.WARNING('ElasticSearch is not available. Skipping initialization.')
            )
            return

        self.stdout.write('Initializing ElasticSearch...')
        
        # Create index if it doesn't exist
        search_service.create_index_if_not_exists()
        
        if search_service.es_available:
            # Sync all existing books
            books = Book.objects.select_related('author').all()
            self.stdout.write(f'Syncing {books.count()} books...')
            
            for book in books:
                search_service.index_book(book)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully synced {books.count()} books to ElasticSearch')
            )
        else:
            self.stdout.write(
                self.style.WARNING('ElasticSearch not available - no books synced')
            )
