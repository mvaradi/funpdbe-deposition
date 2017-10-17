from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UserCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def register(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect('home')
    else:
        form = UserCreateForm()
    return render(request, 'register.html', {'form': form})


@login_required
def home(request):
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('home')