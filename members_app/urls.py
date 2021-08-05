from django.urls import (path, include)
from .views import *
from data_handler.views import (DataListView, SessionDetailsView, DeleteSessionHistoryView, DataListDetailView)

urlpatterns = [
    path("", ProfileOverview.as_view(), name="profile-overview"),
    path("history", RunHistoryView.as_view(), name="profile-run-history"),
    path('membership/', include("membership.urls"), name='membership-urls'),
    path('invoices/', include("invoice_app.urls"), name='members-invoices-app-urls'),
    path("session/<int:pk>", UserSessionDetailsView.as_view(), name="data-handler-user-session-details"),
    path("session/delete/", DeleteSessionHistoryView.as_view(),
         name="data-handler-user-delete-session-history"),
    # path("dashboard", ProfileDashboard.as_view(), name="profile-dashboard"),
    path("activity", ActivityDashboard.as_view(), name="profile-activity"),
    path("inbox", MemberInboxView.as_view(), name="member-inbox"),
    path("settings", AccountSettingsDashboard.as_view(), name="profile-account-settings"),
    path("personal", ProfilePersonal.as_view(), name="profile-personal"),
    path("information", ProfileInformation.as_view(), name="profile-info"),
    path("change-password", ProfileChangePassword.as_view(), name="profile-change-password"),
    path("email", ProfileEmail.as_view(), name="profile-email"),
    path("data/", include([
        path("", DataListView.as_view(), name='data-handler-default'),
        path("<int:pk>/", DataListDetailView.as_view(), name='data-handler-edit-session'),
        path("<int:id>/", SessionDetailsView.as_view(), name='data-handler-session-details'),
    ]), name="members-app-data-list"),

    path("download", download_instructions_template, name='data-handler-temp-download'),
    path("download-dashboard", download_dashboard_pdf, name='profile-dashboard-download'),
]
