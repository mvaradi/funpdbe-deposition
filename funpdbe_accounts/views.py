from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UserCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from .models import RequestedPartner
from .models import PartnerRequestedByUser


def register(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('home')
    else:
        form = UserCreateForm()
    return render(request, 'register.html', {'form': form})


def about(request):
    return render(request, 'about.html')


@login_required
def home(request):
    """
    Home view of the account which lists all the partner resources
    a user contributes to

    There are three distinct lists for specific purposes:
    1.) the list of partner resources for which a given user has
    submission and view permissions. This list is made from Group() objects
    2.) the list of partner resources a given user would like to have permissions.
    This list consists of RequestedPartner() objects
    3.) another list with partner resources (RequestedPartner()) for which
    the user already requested permissions, but it is pending action from
    an administrator
    """

    """
    List of resources associated with a user in PartnerRequestedByUser(),
    but only those for which the corresponding Group() was not yet linked

    In other terms, this is a list of resources to which the user already
    requested permissions, but has not yet been granted by the admin
    """
    pending_requests = []
    requested = PartnerRequestedByUser.objects.select_related().all()
    relevant_requests = requested.filter(user_ref__username__contains=request.user.username)
    for relevant_request in relevant_requests:
        pending_requests.append(relevant_request.partner_ref.partner_name)

    """
    If the user is POSTing requests for new resources to be added to the
    pending list, first check if the resource is already on the list
    
    This should not happen under normal circumstances, but repeated POSTing
    due to refreshing, etc. can do this
    """
    if request.POST:
        for key in request.POST.keys():
            if key != "csrfmiddlewaretoken":
                if key == "remove-pending":
                    partner_name = request.POST.get(key)
                    all_requests = PartnerRequestedByUser.objects.all()
                    all_user_requests = all_requests.filter(user_ref__username__contains=request.user.username)
                    request_to_remove = all_user_requests.filter(partner_ref__partner_name__contains=partner_name)
                    request_to_remove.delete()
                    updated_pending_list = []
                    for i in range(len(pending_requests)):
                        if pending_requests[i] != partner_name:
                            updated_pending_list.append(pending_requests[i])
                    pending_requests = updated_pending_list
                elif key not in pending_requests:
                    partner_resource = RequestedPartner.objects.get(pk=key)
                    new_user_request = PartnerRequestedByUser(user_ref=request.user,
                                                              partner_ref=partner_resource)
                    new_user_request.save()
                    pending_requests.append(key)

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
    List of registered partner groups in RequestedPartner() objects. These 
    objects have no permissions, and after manual curation (!) the corresponding
    Group() object should be created with the same name
    
    This is required so that users can suggests new partner resources, but they
    have to be investigated by an admin on a case to case basis
    """
    user_requests = []
    for partner in RequestedPartner.objects.all():
        if partner.is_active_partner:
            if partner.partner_name not in contributing_to:
                if partner.partner_name not in pending_requests:
                    user_requests.append(partner.partner_name)

    context = {
        "user_name": request.user.username,
        "user_groups": contributing_to,
        "user_pending": pending_requests,
        "user_request": user_requests
    }

    return render(request, 'home.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('home')
