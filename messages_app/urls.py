from django.urls import path
from .views import *

urlpatterns = [
    path("inbox", InboxView.as_view(), name="inbox"),
]