from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
	path('book/<int:book_id>/create/', views.create_review, name='create'),
	path('upvote/<int:review_id>/', views.upvote_review, name='upvote'),
	path('edit/<int:review_id>/', views.edit_review, name='edit'),
	path('delete/<int:review_id>/', views.delete_review, name='delete'),
]

