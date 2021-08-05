from django.contrib import admin
from .models import (Membership, Subscription)

# Register your models here.

admin.site.register(Membership)
# admin.site.register(Plan)
admin.site.register(Subscription)