from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UserCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from .models import FunPdbePartners

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
    """
    Home view of the account which lists all the partner resources
    a user contributes to
    """

    """
    List of partner groups that are Group() objects with certain
    permissions
    """
    contributing_to = []
    groups = Group.objects.select_related().all()
    relevant_groups = groups.filter(user__username__contains=request.user.username)
    for group in relevant_groups:
        contributing_to.append(group.name)

    """
    List of registered partner groups in FunPdbePartners() object. These 
    objects have no permissions, and after manual curation (!) the corresponding
    Group() object should be created with the same name
    
    This is required so that users can suggests new partner resources, but they
    have to be investigated by an admin on a case to case basis
    """
    not_contributing_to = []
    for partner in FunPdbePartners.objects.all():
        if partner.is_active_partner:
            if partner.partner_name not in contributing_to:
                not_contributing_to.append(partner.partner_name)

    account_details = {
        "user_name" : request.user.username,
        "user_groups" : contributing_to,
    }



    return render(request, 'home.html', {'account': account_details, "available_partners": not_contributing_to})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('home')