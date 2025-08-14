from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
	path('book/<int:book_id>/create/', views.create_review, name='create'),
	path('upvote/<int:review_id>/', views.upvote_review, name='upvote'),
]

