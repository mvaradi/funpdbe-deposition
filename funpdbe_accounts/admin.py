from django.contrib import admin
from .models import RequestedPartner
from .models import PartnerRequestedByUser

admin.site.register(PartnerRequestedByUser)
admin.site.register(RequestedPartner)