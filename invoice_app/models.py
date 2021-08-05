from django.db import models
from users.models import Member
# from data_handler.models import MemberDataFile

# "Pending", "Processing", "Draft", "Cancelled", "Completed"

INVOICE_STATUS = (
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("draft", "Draft"),
    ("cancelled", "Cancelled"),
    ("completed", "Completed"),
)


class Invoice(models.Model):
    class Meta:
        db_table = "invoices"

    member = models.ForeignKey(to=Member, on_delete=models.SET_NULL, related_name='all_invoices', null=True)
    invoice_stripe_id = models.CharField(max_length=100, unique=True)
    invoice_pdf_url = models.URLField(null=True, max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)


class Transactions(models.Model):
    class Meta:
        db_table = 'transactions'

    member = models.ForeignKey(to=Member, on_delete=models.SET_NULL, related_name='all_transactions', null=True)
    trans_stripe_id = models.CharField(max_length=100, unique=True)
    invoice_stripe_id = models.CharField(max_length=100, unique=True, null=True)
    receipt_pdf_url = models.URLField(null=True, max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
