from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UserCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import Group


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
    print(request.user.groups)
    groups = Group.objects.select_related().all()
    relevant_groups = groups.filter(user__username__contains=request.user.username)
    account_details = {
        "user_name" : request.user.username,
        "user_groups" : relevant_groups,
        "user_active" : request.user.is_active
    }
    return render(request, 'home.html', {'account': account_details})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('home')