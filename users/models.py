from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from termcolor import cprint

from .managers import CustomUserManager

"""
['id', 'password', 'last_login', 'is_superuser', 'email', 'is_staff', 'is_active', 'date_joined', 'first_name',
'last_name', 'full_name', 'phone', 'street_address', 'state', 'city', 'country', 'zip_code', 'org_name',
'job_title', 'org_website', 'org_type', 'other_org_type', 'annual_revenue', 'total_staff', 'num_of_volunteer',
'num_of_board_members', 'status', 'member_register_token', 'stripe_card_token', 'stripe_customer_id', 'ip_address']
"""

MEMBER_STATUS = (
    ("pending", "Pending"),
    ('active', "Active"),
    ("cancelled", "Cancelled"),
    ("unverified", "Un-Verified")
)

# Just for developments purposes
MEMBERS_TYPES = (
    ('normal_member', 'Normal Member'),
    ('development_member', 'Development Member'),
)


class Member(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    member_type = models.CharField(choices=MEMBERS_TYPES, default=MEMBERS_TYPES[0][0],
                                   max_length=50)  # development only
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=50, null=True, blank=True)
    street_address = models.CharField(max_length=50)
    state = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)
    org_name = models.CharField(max_length=50)
    job_title = models.CharField(max_length=50, blank=True, null=True)
    org_website = models.URLField(max_length=100, blank=True, null=True)
    org_type = models.CharField(max_length=50)
    other_org_type = models.CharField(max_length=50, null=True, blank=True)
    annual_revenue = models.CharField(max_length=200)
    total_staff = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    num_of_volunteer = models.IntegerField(null=True, blank=True)
    num_of_board_members = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=MEMBER_STATUS, default="unverified")
    # membership = models.OneToOneField(to="membership.Membership", null=True, on_delete=models.CASCADE, blank=True)
    member_register_token = models.CharField(max_length=150, null=True, blank=True)
    stripe_card_token = models.CharField(max_length=200, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=200, null=True, blank=True)
    ip_address = models.CharField(max_length=200, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = "members"

    @property
    def get_fields_as_list(self):
        fields = self._meta.fields
        fields_list = []
        for fid in fields:
            fields_list.append(fid.name)
        return fields_list

    @property
    def get_member_info_as_dict(self):
        subscription_obj = self.member_subscription.get()
        data_handler_obj = self.member_data_file.filter().first()
        data_usage_obj = self.data_usage.filter().first()
        membership_obj = subscription_obj.stripe_plan_id
        range_label = membership_obj.range_label
        all_records_count = data_handler_obj.data_sessions_set.filter(is_run_model=True).values_list(
            'all_records_count', flat=True)
        all_data_usage = sum(all_records_count) + data_usage_obj.records_used if data_usage_obj else 0
        data_usage_per = 0
        if all_data_usage != 0:
            # cprint(all_data_usage, "yellow")
            data_usage_per = all_data_usage / membership_obj.allowed_records_count
            data_usage_per = data_usage_per * 100
            # cprint(data_usage_per * 100, 'cyan')
        return {
            "id": self.pk,
            "last_login": self.last_login,
            'email': self.email,
            "status": self.status,
            "is_active": self.is_active,
            'date_joined': self.date_joined,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'street_address': self.street_address,
            'state': self.state,
            'city': self.city,
            'country': self.country,
            'zip_code': self.zip_code,
            'org_name': self.org_name,
            'job_title': self.job_title,
            'org_website': self.org_website,
            'org_type': self.org_type,
            'other_org_type': self.other_org_type,
            'annual_revenue': self.annual_revenue,
            'total_staff': self.total_staff,
            'num_of_volunteer': self.num_of_volunteer,
            'num_of_board_members': self.num_of_board_members,
            "membership": subscription_obj.stripe_plan_id.parent,
            "subscription_range": subscription_obj.stripe_plan_id.range_label,
            'data_usage': data_usage_obj.records_used if data_usage_obj else 0,
            'run_modal_times': len(all_records_count),
            'data_usage_per': data_usage_per,
            'range_label': range_label
        }


class UnverifiedMember(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "unverified_member"
