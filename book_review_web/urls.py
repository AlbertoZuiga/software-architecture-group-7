"""
URL configuration for book_review_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.books.views import books_delete  # alias direct import for un-namespaced route
from apps.common.views import signup

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="auth/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/signup/", signup, name="signup"),
    path("", include("apps.common.urls")),
    path("books/", include("apps.books.urls")),
    # Un-namespaced legacy alias for book delete (to satisfy templates expecting 'delete')
    path("books/<int:book_id>/delete/", books_delete, name="delete"),
    path("authors/", include("apps.authors.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("book/<int:book_id>/sales/", include("apps.sales.urls")),
    path("stats/", include("apps.stats.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
