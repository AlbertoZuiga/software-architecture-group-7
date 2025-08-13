from django.urls import path
from . import views

app_name = "books"

urlpatterns = [
    path('', views.books_index, name='index'),
    path('<int:book_id>/', views.books_show, name='show'),
]
