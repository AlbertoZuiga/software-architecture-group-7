from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("books:index")
    else:
        form = UserCreationForm()
    return render(request, "auth/signup.html", {"form": form})


def home(request):
    return render(request, "home.html")
