from django.urls import path, include
from .views import *

urlpatterns = [
    path("", AdminProfileOverview.as_view(), name="admin-profile-overview"),
    path("personal", AdminProfilePersonal.as_view(), name="admin-profile-personal"),
    path("information", AdminProfileInformation.as_view(), name="admin-profile-info"),
    path("change-password", AdminProfileChangePassword.as_view(), name="admin-profile-change-password"),
]