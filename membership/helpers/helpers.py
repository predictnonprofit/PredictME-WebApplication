import os
import traceback

import stripe
from termcolor import cprint

from predict_me.helpers import check_internet_access
from predict_me.my_logger import log_exception
from users.models import Member

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def get_subscription_and_membership(member: Member):
    """
    This function will return the subscription and membership objects for any member,
    and will handler administrator account issue because admin has no membership and subscription objects
    """
    try:
        member_data = dict()
        member_data["is_superuser"] = member.is_superuser
        subscription_obj = member.subscription.filter().first()
        if subscription_obj is not None:
            # this case the user not administrator account
            data_handler_obj = member.member_data_file.filter().first()
            member_data['subscription_obj'] = subscription_obj
            member_data["membership_obj"] = subscription_obj.membership
            member_data['data_handler_obj'] = data_handler_obj
            member_data['data_handler_session'] = data_handler_obj.data_sessions_set.filter().all()
        else:
            # this case the user is administrator account
            member_data['subscription_obj'] = None
            member_data["membership_obj"] = None
            member_data['data_handler_obj'] = None
            member_data['data_handler_session'] = None

        return member_data
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_member_total_charges(member: Member):
    """
    This function will calculate the total charges for the member from stripe
    """
    all_charge_amount = []
    subscription_obj = member.subscription.filter().first()
    if subscription_obj is not None:
        check_connection = check_internet_access()  # just for developments
        if check_connection is True:
            stripe_token = subscription_obj.stripe_customer_id
            charges = stripe.Charge.list(customer=stripe_token)
            for charge in charges:
                all_charge_amount.append(float(charge.get('amount')) / 100)
            return {'all_charges_amount': sum(all_charge_amount), "charges_sum": len(all_charge_amount)}
        else:
            return {}
