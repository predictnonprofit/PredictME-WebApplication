import traceback
from membership.models import (Membership, Subscription)
from data_handler.models import (DataFile, DataHandlerSession)
from site_settings.models import CompanySettings
from crash_reporting.models import CrashReport
from members_app.helper import calculate_records_left_percentage
from django.core.cache import cache
import stripe
from membership.helpers import get_subscription_and_membership
from predict_me.helpers import check_internet_access
from predict_me.my_logger import log_exception
import json
from django.core.serializers.json import DjangoJSONEncoder
from crash_reporting.forms import CrashReportForm
from termcolor import cprint
from prettyprinter import (cpprint, pprint)
from django.conf import settings


# from predict_me.helpers import quick_print, set_permissions_and_groups_to_members


def get_user_subscription(request):
    if request.user.is_authenticated:

        try:
            subscription_obj = Subscription.objects.get(member_id=request.user)
        except Subscription.DoesNotExist:
            subscription_obj = None
        return subscription_obj


def get_data_handler_obj(request):
    if request.user.is_authenticated:

        # check if the user is administrator account
        if request.user.is_superuser is not True:
            data_handler_obj = DataFile.objects.get(member=request.user)
            return data_handler_obj


def get_data_handler_and_session(request):
    if request.user.is_authenticated:
        data_handler_obj = DataFile.objects.filter(member=request.user).first()
        data_session_obj = DataHandlerSession.objects.filter(data_handler_id=data_handler_obj).first()
        return {
            "data_obj": data_handler_obj,
            "session_obj": data_session_obj
        }


def get_all_member_objects(request):
    """
    this function will return dictionary of all user data (subscription, data handler, data handler session, and member) objects
    """
    member = request.user
    if request.user.is_authenticated:
        all_objs = {}
        records_left = 0
        member_data = get_subscription_and_membership(member)
        data_handler_obj = member_data.get("data_handler_obj")
        data_handler_session = member_data.get("data_sessions_set")
        data_usage = member.data_usage.filter().first()
        records_left = calculate_records_left_percentage(data_handler_obj, data_handler_session)
        all_objs['SUBSCRIPTION'] = member_data.get("subscription_obj")
        all_objs['MEMBERSHIP'] = member_data.get('membership_obj')
        all_objs['MEMBER'] = member
        all_objs['DATA_HANDLER'] = data_handler_obj
        all_objs['DATA_HANDLER_SESSION'] = data_handler_session
        all_objs['RECORDS_LEFT'] = records_left
        all_objs['DATA_USAGE'] = data_usage
        return all_objs


def check_member_if_allowed_to_run_pm_model(request):
    """
    this function will check if the user allowed to run the model, will check the user data usage, if above the limited or not
    """
    member = request.user

    # check if the user is is_anonymous user
    if member.is_anonymous is not True:
        member_data = get_subscription_and_membership(member)
        subscription_obj = member_data.get('subscription_obj')
        membership_obj = member_data.get('membership_obj')
        data_handler_obj = member_data.get("data_handler_obj")
        # check if data handler object is not None
        if data_handler_obj is not None:
            all_records_count = data_handler_obj.data_sessions_set.filter(is_run_model=False).values_list(
                'all_records_count', flat=True)
            all_records_count = sum(list(all_records_count))
            # check if the user has membership, this for registered users
            if membership_obj is not None:
                allowed_records_count = int(membership_obj.allowed_records_count)
                data_usage_obj = member.data_usage.filter().first()
                if data_usage_obj is not None:
                    data_usage = int(data_usage_obj.records_used)
                    total_data_usage = int(data_usage + all_records_count)  # this with not complete sessions
                    if total_data_usage < allowed_records_count:
                        return True
                    else:
                        return False
                else:
                    return True
        else:
            return False


def get_stripe_details(request):
    """
    This function will retrieve all stripe details of the logged in user, and save it in the cache
    """
    try:
        member = request.user
        data = dict()

        # check if the stripe_data exists in cache
        if bool(cache.get("stripe_data")) is False:
            # check if internet connection available
            if check_internet_access() is True:
                # check if the user is is_anonymous user
                if member.is_anonymous is not True:
                    subscription_obj = member.subscription.filter().first()
                    if subscription_obj is not None:
                        try:
                            stripe_card_obj = stripe.Customer.retrieve_source(
                                subscription_obj.stripe_customer_id,
                                subscription_obj.stripe_card_id,
                            )
                            # check if the user has data on stripe, to avoid any error in registration process
                            if stripe_card_obj.get('data'):
                                data['last4'] = stripe_card_obj['last4']
                                stripe_customer = stripe.Customer.retrieve(
                                    subscription_obj.stripe_customer_id)  # enable this
                                data['s_name'] = stripe_customer['name']  # enable this
                                data['card_token'] = stripe_customer.get('default_source')
                                data['s_email'] = stripe_customer.get('email')
                                data['subscription_id'] = stripe_customer.get('subscriptions').get('data')[0].get('id')
                                data['status'] = stripe_customer.get('subscriptions').get('data')[0].get('status')
                                data['current_period_start'] = stripe_customer.get('subscriptions').get('data')[0].get(
                                    'current_period_start')
                                data['current_period_end'] = stripe_customer.get('subscriptions').get('data')[0].get(
                                    'current_period_end')

                            cache.set('stripe_data', data)
                            return cache.get("stripe_data")
                        except stripe.error.InvalidRequestError:
                            cprint(traceback.format_exc(), 'red')
                            log_exception(traceback.format_exc())

                        except Exception as ex:
                            cprint(traceback.format_exc(), 'red')
                            log_exception(traceback.format_exc())
            else:

                cache.set('stripe_data', {'msg': 'No Internet Connection Available!'})
        else:

            return cache.get("stripe_data")

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_all_memberships(request):
    try:
        all_memberships = {}
        # all_memberships_obj = Membership.objects.filter(parent__isnull=True)
        all_memberships_obj = Membership.objects.all()
        for membership in all_memberships_obj:
            all_memberships[membership.slug] = {
                'slug': membership.slug,
                "monthly_fee": membership.monthly_fee,
                "yearly_fee": membership.yearly_fee,
                "day_price": membership.day_price,
                "additional_fee": membership.additional_fee_per_extra_record,
                "allowed_records_count": membership.allowed_records_count,
            }

        # cpprint(all_memberships, end="\n")
        return all_memberships

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_user_membership_only(request):
    try:
        if request.user.is_authenticated and not request.user.is_superuser:
            subscription_obj = request.user.subscription.filter().first()
            if subscription_obj is not None:
                # check if the user has membership, to avoid any error in registration process
                if subscription_obj.membership is not None:
                    return subscription_obj.membership.parent
                    # return 'professional'

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_company_settings(request):
    """
    This will use globally to access company details
    """
    try:

        settings = CompanySettings.objects.values()
        settings = json.dumps(list(settings), cls=DjangoJSONEncoder)
        settings = json.loads(settings)
        settings = settings[0]
        return settings
    except IndexError:
        return {}
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_crash_reporting_form(request):
    try:
        # url_path = {"url": request.build_absolute_uri()}
        crash_form = CrashReportForm(request=request)
        return crash_form
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_administrator_top_navbar_total_badges(request):
    try:
        data = {}
        crash_reports_total = CrashReport.objects.filter(is_seen=False)
        data['total_new_reports'] = int(crash_reports_total.count())
        return data
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def is_administrator_user(request):
    if request.user.is_authenticated:
        return request.user.groups.filter(name='Administrator').exists()


def is_debug_mode(request):
    return settings.DEBUG


def return_all_context(request):
    return {
        "get_user_membership": get_user_subscription(request),  # fix this in all places that call it
        "get_data_handler_obj": get_data_handler_obj(request),
        "get_all_member_info": get_all_member_objects(request),
        "get_data_handler_and_session": get_data_handler_and_session(request),
        'check_member_if_allowed_to_run_pm_model': check_member_if_allowed_to_run_pm_model(request),
        "get_stripe_details": get_stripe_details(request),
        'get_all_memberships': get_all_memberships(request),
        "get_user_membership_only": get_user_membership_only(request),
        "get_company_settings": get_company_settings(request),
        'crash_report_form': get_crash_reporting_form(request),
        "admin_top_navbar_total": get_administrator_top_navbar_total_badges(request),
        'is_administrator_user': is_administrator_user(request),
        "is_debug_mode": is_debug_mode(request)
    }
