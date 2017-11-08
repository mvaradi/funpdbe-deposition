from django.contrib import admin
from .models import RequestedPartner
from .models import PartnerRequestedByUser

admin.site.register(PartnerRequestedByUser)

@admin.register(RequestedPartner)
class RequestedPartnerAdmin(admin.ModelAdmin):
    pass