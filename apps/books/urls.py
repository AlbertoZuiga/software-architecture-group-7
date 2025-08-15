from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("", views.books_index, name="index"),
    path("create/", views.books_create, name="create"),
    path("<int:book_id>/", views.books_show, name="show"),
    path("<int:book_id>/update/", views.books_update, name="update"),
]
