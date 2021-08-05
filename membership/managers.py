from django.db import models


class SubscribeManager(models.Manager):

    def get_all_yearly_users(self):
        queryset = self.get_queryset()
        all_rows = queryset.filter(sub_range="yearly")
        return all_rows

    def get_all_monthly_users(self):
        queryset = self.get_queryset()
        all_rows = queryset.filter(sub_range="monthly")
        return all_rows
