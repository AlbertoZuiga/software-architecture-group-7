import logging
from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchVector

logger = logging.getLogger(__name__)

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    logger.warning("ElasticSearch not available. Falling back to database search.")


class SearchService:
    def __init__(self):
        self.es_client = None
        self.es_available = False
        
        if ELASTICSEARCH_AVAILABLE:
            try:
                es_host = getattr(settings, 'ELASTICSEARCH_HOST', 'localhost')
                es_port = getattr(settings, 'ELASTICSEARCH_PORT', 9200)
                
                self.es_client = Elasticsearch([f'http://{es_host}:{es_port}'])
                
                # Test connection
                if self.es_client.ping():
                    self.es_available = True
                    logger.info("ElasticSearch connection established")
                else:
                    logger.warning("ElasticSearch ping failed. Using database search.")
            except Exception as e:
                logger.warning(f"ElasticSearch connection failed: {e}. Using database search.")
    
    def index_book(self, book):
        if not self.es_available:
            return
        
        try:
            doc = {
                'id': book.id,
                'name': book.name,
                'summary': book.summary,
                'author_name': book.author.name,
                'published_at': book.published_at.isoformat() if book.published_at else None,
                'total_sales': book.total_sales,
            }
            
            self.es_client.index(
                index='books',
                id=book.id,
                body=doc
            )
            logger.debug(f"Book {book.id} indexed in ElasticSearch")
        except Exception as e:
            logger.error(f"Failed to index book {book.id}: {e}")
    
    def delete_book(self, book_id):
        if not self.es_available:
            return
        
        try:
            self.es_client.delete(
                index='books',
                id=book_id,
                ignore=[404] 
            )
            logger.debug(f"Book {book_id} deleted from ElasticSearch")
        except Exception as e:
            logger.error(f"Failed to delete book {book_id}: {e}")
    
    def search_books(self, query, queryset=None):
        if not query or not query.strip():
            return queryset if queryset is not None else []
        
        if self.es_available:
            return self._elasticsearch_search(query, queryset)
        else:
            return self._database_search(query, queryset)
    
    def _elasticsearch_search(self, query, queryset):
        try:
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name^2", "summary", "author_name"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "size": 1000,  
                "_source": ["id"]
            }
            
            response = self.es_client.search(
                index='books',
                body=search_body
            )
            
            book_ids = [hit['_source']['id'] for hit in response['hits']['hits']]
            
            if queryset is not None:
                return queryset.filter(id__in=book_ids)
            else:
                return book_ids
                
        except Exception as e:
            logger.error(f"ElasticSearch search failed: {e}. Falling back to database search.")
            return self._database_search(query, queryset)
    
    def _database_search(self, query, queryset):
        """Fallback database search using PostgreSQL full-text search"""
        from apps.books.models import Book
        
        if queryset is None:
            queryset = Book.objects.all()
        
        vector = SearchVector("summary", "name", "author__name")
        search_query = SearchQuery(query)
        return queryset.annotate(search=vector).filter(search=search_query)
    
    def create_index_if_not_exists(self):
        """Create the books index if it doesn't exist"""
        if not self.es_available:
            return
        
        try:
            if not self.es_client.indices.exists(index='books'):
                mapping = {
                    "mappings": {
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "summary": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "author_name": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "published_at": {"type": "date"},
                            "total_sales": {"type": "integer"}
                        }
                    }
                }
                
                self.es_client.indices.create(index='books', body=mapping)
                logger.info("Books index created in ElasticSearch")
        except Exception as e:
            logger.error(f"Failed to create ElasticSearch index: {e}")

search_service = SearchService()
