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
    member = models.ForeignKey(to=Member, on_delete=models.SET_NULL, related_name='all_invoices', null=True)
    invoice_stripe_id = models.CharField(max_length=100, unique=True)
    invoice_pdf_url = models.URLField(null=True, max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "invoices"

    def __str__(self):
        return f"Invoice for {self.member}"


class Transactions(models.Model):
    member = models.ForeignKey(to=Member, on_delete=models.SET_NULL, related_name='all_transactions', null=True)
    trans_stripe_id = models.CharField(max_length=100, unique=True)
    invoice_stripe_id = models.CharField(max_length=100, unique=True, null=True)
    receipt_pdf_url = models.URLField(null=True, max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'

    def __str__(self):
        return f"Transaction for {self.member}"


class Charges(models.Model):
    member = models.ForeignKey(to=Member, on_delete=models.CASCADE, related_name='charges', db_index=True)
    charge_token = models.CharField(max_length=100, unique=True)
    amount = models.BigIntegerField(null=True, blank=True)
    # invoice_token = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    charge_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "charges"

    def __str__(self):
        return f"Charge Object for {self.member}"
