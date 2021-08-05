from django.urls import path
from .views import ListActivitiesView

urlpatterns = [
    path("", ListActivitiesView.as_view(), name="activity-list"),
]
