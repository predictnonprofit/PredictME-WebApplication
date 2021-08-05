from django.urls import path, include
from .views import *

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard-home"),
    path("users/", include("dash_users.urls"), name="users-urls"),
    # path("dashboard/profile/", include("members_app.urls"), name="profile-urls"),
    path("data/", include("data_handler.urls"), name="data-urls"),
    path("data-manage/", include("data_handler_admin.urls"), name="data-manage-urls"),
    path("invoice/", include("invoice_app.urls"), name="invoice-urls"),
    path("messages/", include("messages_app.urls"), name="messages-urls"),
    path("settings/", include("site_settings.urls"), name="settings-urls"),
    path("activities/", include("activity_app.urls"), name="activity-urls"),
    path("reports/", include("reports_app.urls"), name="reports-urls"),
    path("admin/profile/", include("admin_profile.urls"), name="admin-profile-urls"),
    path('crashes/', include('crash_reporting.urls'), name="crashed-urls"),

]
