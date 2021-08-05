from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    path("", ReportsListView.as_view(), name="reports-list-view"),
    path("testing", testing_reports, name="reports-test-view"),
    path("users", ReportsUsersListView.as_view(), name="reports-users-list-view"),
    path("users-status", ReportsUserStatusListView.as_view(), name="reports-users-status-list-view"),
    path("data-usage", ReportsDataUsageView.as_view(), name="reports-data-usage-list-view"),
    path("extra-records", ReportsExtraUsageView.as_view(), name="reports-extra-usage-list-view"),
    path("profit-share", ProfitShareView.as_view(), name="reports-profit-share-list-view"),
    path("revenues", ReportsRevenuesView.as_view(), name="reports-revenues"),
    path("api/", include([
        path("fetch", FetchReports.as_view(), name="reports-api-fetch"),
        path("filters", FilterReports.as_view(), name="reports-api-filter"),
        path("fetch-custom-report-data", FetchReportData.as_view(), name="reports-api-custom-column-data"),
    ]), name="reports-api"),
]
