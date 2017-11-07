from django.db import models


class FunPdbePartners(models.Model):

    partner_name = models.CharField("Partner resource name", max_length=100, primary_key = True)
    partner_owner = models.CharField("Owner of the resource", max_length=255)
    partner_contact = models.EmailField("Contact email address", max_length=255)
    work_package = models.IntegerField("Work package", null=True)
    is_active_partner = models.BooleanField("Actively participating resource", default=True)

