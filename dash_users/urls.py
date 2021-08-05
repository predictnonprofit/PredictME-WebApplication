from django.urls import path, include
from .views import *

urlpatterns = [
    path("", UsersListView.as_view(), name="admin-users-list"),
    path("create", UsersCreateView.as_view(), name="admin-users-create"),
    path("details/<int:pk>", UsersDetailsView.as_view(), name="admin-users-details"),
    path("list-pending", UsersPendingView.as_view(), name="admin-users-pending"),
    path("test-delete", delete_members, name="admin-users-remove"),
    path("api/", include([
        path("fetch-member-details", FetchMemberDetailsView.as_view(), name="api-fetch-member-details-crash-report"),
        path("delete-member", DeleteMemberView.as_view(), name="api-delete-member-details-crash-report"),
    ]), name='dash-users-api-urls'),
]