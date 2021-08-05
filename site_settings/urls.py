from django.urls import path
from .views import *

urlpatterns = [
    path("company", CompanySettingsView.as_view(), name="settings-company"),
    path("about", AboutSettingsView.as_view(), name="settings-about"),
    path("plans", PlansSettingsView.as_view(), name="settings-plans"),

]