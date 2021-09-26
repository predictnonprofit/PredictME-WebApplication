from django.urls import path, include
from .views import *

urlpatterns = [
    path("update-credit-card", UpdateStripeCreditCardView.as_view(), name="membership-account-update-credit-card"),
    # check where this used in template files don't delete the class view
    # path("upgrade-membership", UpgradeMembershipView.as_view(), name='membership-upgrade-membership'),
    path("charge-extra-records", ChargeExtraRecordView.as_view(), name='membership-charge-extra-records'),
    path("change-stripe-card", ChangeStripeCardView.as_view(), name='membership-change-stripe-card'),
    path("api/", include([
        path("upgrade-membership-api-only", UpgradeMembershipAPIView.as_view(), name='api-upgrade-membership-only')
    ]), name='membership-api-urls')
]
