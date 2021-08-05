from django.db import models


class CompanySettings(models.Model):
    slug = models.SlugField(unique=True, db_index=True, default="company")
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, max_length=100)
    phone = models.CharField(null=True, blank=True, max_length=100)
    logo = models.FileField(null=True, blank=True, upload_to="media/logo")
    url = models.URLField(null=True, blank=True, max_length=120)
    description = models.CharField(null=True, blank=True, max_length=255)
    keywords = models.CharField(null=True, blank=True, max_length=255)
    status = models.BooleanField(null=True, blank=True, default=True)
    close_msg = models.CharField(max_length=255, blank=True, null=True)
    admin_name = models.CharField(max_length=50, null=True, blank=True)
    admin_email = models.EmailField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "company_settings"


# class AboutSettings(models.Model):
#     text = models.TextField(null=True, blank=True)
