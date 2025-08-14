from django.urls import path

from . import views

app_name = "authors"

urlpatterns = [
    path("", views.authors_index, name="index"),
    path("create/", views.authors_create, name="create"),
    path("<int:author_id>/", views.authors_show, name="show"),
    path("<int:author_id>/update/", views.authors_update, name="update"),
]
