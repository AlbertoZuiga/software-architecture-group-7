from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
	path('book/<int:book_id>/create/', views.create_review, name='create'),
]