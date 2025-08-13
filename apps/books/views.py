from django.http import HttpResponse
from django.shortcuts import render
from .models import Book

def books_index(request):
    books = Book.objects.all()
    return render(request, 'books/books_index.html', {'books': books})

def books_show(request, book_id):
    book = Book.objects.get(id=book_id)
    return render(request, 'books/books_show.html', {'book': book})
