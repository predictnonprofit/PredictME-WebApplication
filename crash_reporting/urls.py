# -*- coding: utf-8 -*-#
from django.urls import (path, include)
from .views import *

urlpatterns = [
    path("list", CrashReportsListView.as_view(), name="crashes-list-url"),
    path("details/<int:pk>", CrashReportsDetailsView.as_view(), name="crashes-details-url"),
    path("report-crash", ReportCrashView.as_view(), name='crash-report-url'),
    path("api/", include([
        path("change-report-status", ChangeCrashReportStatusView.as_view(), name="api-change-status-crash-report"),
    ]), name='crash-report-api-urls'),
]
