from django.urls import (path, include)
from .views import *

urlpatterns = [
    path("details", InvoiceDetailsView.as_view(), name="invoice-details"),
    path("list", InvoiceListView.as_view(), name="invoice-list"),
    path("create", InvCreateView.as_view(), name="invoice-create"),
    path("print", InvoicePrintView.as_view(), name='invoice-print'),
    # path("download", InvoiceDownloadView.as_view(), name='invoice-download'),

    path("members/api/", include([
        path("grab-member-invoices", GrabMemberInvoices.as_view(), name="invoice-api-member-grab-invoices"),
        path("grab-member-transactions", GrabMemberTransactions.as_view(), name="invoice-api-member-grab-transactions"),

    ])),

]
