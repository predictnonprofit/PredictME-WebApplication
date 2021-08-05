from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    path("", DataHandlerManageListView.as_view(), name="data-handler-manage-list"),
    path("details", DataHandlerManageDetailsView.as_view(), name="data-handler-manage-details"),
]

