from django.urls import path

from . import views

app_name = "sales"

urlpatterns = [
    path("", views.sales_index, name="index"),
    path('create/', views.sales_create, name='create'),
]
