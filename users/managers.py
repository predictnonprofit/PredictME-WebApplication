from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

    def get_active_users(self):
        queryset = self.get_queryset()
        all_data = queryset.filter(status="active")
        return all_data

    def get_unverified_users(self):
        queryset = self.get_queryset()
        all_data = queryset.filter(status="unverified")
        return all_data

    def get_pending_users(self):
        queryset = self.get_queryset()
        all_data = queryset.filter(status="pending")
        return all_data

    def get_canceled_users(self):
        queryset = self.get_queryset()
        all_data = queryset.filter(status="canceled")
        return all_data

    def get_all_users(self):
        queryset = self.get_queryset()
        all_data = queryset.all()
        return all_data

    def get_users_by_register_date(self, full_date_range: str):
        queryset = self.get_queryset()
        start_date, end_date = full_date_range.split(" - ")
        all_data = queryset.filter(date_joined__range=[start_date, end_date])
        return all_data
