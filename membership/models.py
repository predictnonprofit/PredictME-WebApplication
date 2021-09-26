from django.db import models
from .managers import SubscribeManager
from users.models import Member

MEMBERSHIP_LABELS = (
    ("starter", "Starter"),
    ("professional", "Professional",),
    ("expert", "Expert"),
    ("starter_monthly", "Starter Monthly"),
    ("starter_yearly", "Starter Yearly"),
    ("professional_monthly", "Professional Monthly"),
    ("professional_yearly", "Professional Yearly"),
    ("expert_monthly", "Expert Monthly"),
    ("expert_yearly", "Expert Yearly"),
    ("unlimited", "Unlimited (development)"),
)

PARENTS_MEMBERSHIP_LABELS = (
    ("starter", "Starter"),
    ("professional", "Professional",),
    ("expert", "Expert"),
    ("unlimited_development", "Unlimited (Development)"),
)

SUB_RANGE = (
    ("monthly", "Monthly"),
    ("yearly", "Yearly"),
)


class Membership(models.Model):
    slug = models.SlugField(null=True, blank=True, db_index=True)
    membership_type = models.CharField(choices=MEMBERSHIP_LABELS, max_length=30, null=True, blank=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    yearly_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    day_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stripe_plane_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=100, null=True, blank=True)
    additional_fee_per_extra_record = models.DecimalField(max_digits=2, decimal_places=2, null=True, blank=True)
    allowed_records_count = models.BigIntegerField(null=True, blank=True)
    parent = models.CharField(choices=PARENTS_MEMBERSHIP_LABELS, max_length=30, null=True, blank=True)
    range_label = models.CharField(max_length=20, choices=SUB_RANGE, null=True, blank=True)

    class Meta:
        db_table = "membership"

    def __str__(self):
        return f"Membership {self.slug}"

    @property
    def get_fields_as_list(self):
        fields = self._meta.fields
        fields_list = []
        for fid in fields:
            fields_list.append(fid.name)
        return fields_list


class Subscription(models.Model):
    objects = SubscribeManager()
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="subscription", null=True,
                               blank=True, related_query_name="member_subscription")
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_card_token = models.CharField(max_length=200, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=60, null=True, blank=True)
    # stripe_plan_id = models.ForeignKey(Membership, on_delete=models.CASCADE, blank=True, null=True)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="membership", blank=True,
                                   null=True)
    subscription_status = models.BooleanField(null=True, blank=True)
    subscription_period_start = models.DateTimeField(null=True, blank=True)
    subscription_period_end = models.DateTimeField(null=True, blank=True)
    card_expire = models.DateTimeField(null=True, blank=True)
    stripe_card_id = models.CharField(max_length=50, null=True, blank=True)
    last_invoice_id = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "subscriptions"

    def __str__(self):
        return f"Subscription Object for {self.member}"

    @property
    def get_fields_as_list(self):
        fields = self._meta.fields
        fields_list = []
        for fid in fields:
            fields_list.append(fid.name)
        return fields_list
