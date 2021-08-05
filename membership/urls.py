from django.urls import path
from .views import *

urlpatterns = [
    path("update-stripe", UpdateStripeView.as_view(), name="membership-account-update-stripe"),
    path("upgrade-membership", UpgradeMembershipView.as_view(), name='membership-upgrade-membership'),
    path("charge-extra-records", ChargeExtraRecordView.as_view(), name='membership-charge-extra-records'),
    path("change-stripe-card", ChangeStripeCardView.as_view(), name='membership-change-stripe-card'),
]
