from django.urls import path
from . import views

app_name = "authors"

urlpatterns = [
    path('', views.authors_index, name='index'),
    path('<int:author_id>/', views.authors_show, name='show'),
]
