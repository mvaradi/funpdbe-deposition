from django.db import models
from django.contrib.auth.models import User


class RequestedPartner(models.Model):
    """
    This model stores information on potential partner resources
    suggested by users. This is uncoupled from the Group() model,
    because all of these suggestions have to be manually examined
    before creating a corresponding Group() which will have certain
    API permissions
    """

    partner_name = models.CharField("Partner resource name",
                                    max_length=100,
                                    primary_key=True)
    partner_owner = models.CharField("Owner of the resource",
                                     max_length=255)
    partner_contact = models.EmailField("Contact email address",
                                        max_length=255)
    partner_url = models.URLField("URL of the resource",
                                  null=True)
    partner_description = models.TextField("Description of the resource",
                                           null=True)
    work_package = models.IntegerField("Work package",
                                       null=True)
    is_active_partner = models.BooleanField("Actively participating resource",
                                            default=True)

    def __str__(self):
        return self.partner_name


class PartnerRequestedByUser(models.Model):
    """
    Intermediate model connecting users to requested partner resources
    """

    user_ref = models.ForeignKey(User,
                                 verbose_name="User requesting access to partner resource")
    partner_ref = models.ForeignKey(RequestedPartner,
                                    verbose_name="Requested partner resource")

    def __str__(self):
        return "%s requests %s" % (self.user_ref.username, self.partner_ref.partner_name)