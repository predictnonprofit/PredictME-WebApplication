import copy
import json
import os
import traceback
from datetime import datetime, date

import pytz
import stripe
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import (redirect, reverse)
from django.views.generic import TemplateView
from prettyprinter import cpprint
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from termcolor import cprint

from data_handler.helpers import get_data_table_overview
from invoice_app.models import Charges
from predict_me.helpers import check_internet_access
from predict_me.my_logger import log_exception
from users.models import Member
from .models import Membership

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "membership/checkout.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stripe_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        subscription = self.request.user.subscription.get()
        context['subscription'] = subscription
        context['stripe_key'] = stripe_key
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # check if there is any internet connection errors
            if check_internet_access() is True:
                # internet connection available
                member = request.user
                subscription = member.subscription.select_for_update().get()
                # cpprint(request.POST, end="\n")
                sub_range = request.POST.get("sub_range")
                payment_agree = request.POST.get("agree_payment")
                stripe_token = request.POST.get("stripeToken")
                subscription.stripe_card_token = stripe_token
                # cprint(f"Before {member.status}", 'blue')
                member.status = "active"

                # id, created, plan[interval], plan[product], price[active], latest_invoice, status, current_period_end
                # current_period_start, customer

                # start save the membership monthly or yearly to db
                membership = Membership.objects.filter(
                    Q(range_label=sub_range) & Q(parent=subscription.membership.slug)).first()
                cprint("Here membership view: ", 'red')
                cprint(membership, "yellow")
                subscription.membership = membership
                # subscription = subscription.save(commit=False)

                # update member token in stripe with new card token
                customer = stripe.Customer.modify(
                    subscription.stripe_customer_id,
                    card=stripe_token
                )
                subscription.stripe_customer_id = customer['id']

                # create subscription object for customer in stripe
                stripe_subscription_obj = stripe.Subscription.create(
                    customer=customer['id'],
                    items=[
                        {"price": subscription.membership.stripe_price_id},
                    ],
                )

                # latest_invoice
                latest_invoice_id = stripe_subscription_obj.to_dict().get("latest_invoice")

                # fetch member info from stripe
                tmp_customer = stripe.Customer.retrieve(customer['id'])
                card_id = tmp_customer['default_source']
                subscription.stripe_subscription_id = stripe_subscription_obj['id']
                subscription.stripe_card_id = card_id
                card_obj = stripe.Customer.retrieve_source(customer['id'], card_id)  # fetch card object
                start_date = datetime.fromtimestamp(stripe_subscription_obj['current_period_start'],
                                                    tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                end_date = datetime.fromtimestamp(stripe_subscription_obj['current_period_end'],
                                                  tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                subscription.subscription_status = True if stripe_subscription_obj['status'] == "active" else False
                subscription.subscription_period_start = start_date
                subscription.subscription_period_end = end_date
                subscription.card_expire = datetime(card_obj['exp_year'], card_obj['exp_month'], 1)
                subscription.last_invoice_id = latest_invoice_id
                # subscription.sub_range = sub_range

                cprint(f"After {member.status}", 'cyan')
                member.save()
                subscription.save()
                messages.success(request, "Saved all subscription and membership data to db successfully!")
                return redirect(reverse("register_successfully"))
            else:
                # no internet connection avaliable
                messages.error(request, "No Internet Connection!, try again later.", 'danger')
                return redirect(reverse("register_successfully"))
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, "Error In checkout!")


class UpdateStripeCreditCardView(LoginRequiredMixin, TemplateView):
    login_url = "login"
    template_name = 'members_app/profile/account_settings.html'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # old -> card_1Jctw4CXFX3jJJ8KJJ2Rtv7j

            # cprint(request.POST.keys(), 'yellow')
            # cpprint(request.POST)
            tmp_data = request.POST.copy()
            tmp_data.update({
                "view_name": "membership-account-update-stripe"
            })
            # return JsonResponse(data=tmp_data, status=status.HTTP_200_OK)
            # return Response(data=tmp_data, status=status.HTTP_200_OK)
            # check internet connection available
            if check_internet_access() is True:
                member = request.user
                member_subscription = member.subscription.select_for_update().get()
                old_stripe_customer_data = stripe.Customer.retrieve(member_subscription.stripe_customer_id)
                old_stripe_subscription_data = stripe.Subscription.retrieve(member_subscription.stripe_subscription_id)
                # cpprint(old_stripe_customer_data.to_dict(), end="\n")
                # cpprint(old_stripe_subscription_data.to_dict(), end="\n")
                # cpprint(old_stripe_customer_data, end="\n")
                tmp_data.update({"old_stripe_customer_data": old_stripe_customer_data.to_dict()})
                tmp_data.update({"old_stripe_subscription_data": old_stripe_subscription_data.to_dict()})

                # cprint(member_subscription, "cyan")
                subscription_backup = copy.deepcopy(member_subscription)
                stripe_token = request.POST.get("stripeToken")
                full_name = request.POST.get("full_name")
                # new_membership = Membership.objects.filter(slug='starter_monthly').first()
                stripe_customer = stripe.Customer.modify(
                    member_subscription.stripe_customer_id,
                    source=stripe_token,
                    name=full_name
                )
                cprint('stripe_customer ok', 'green')
                # latest_invoice
                latest_invoice_id = stripe_customer.to_dict().get("subscriptions").get("data")[0].get('latest_invoice')

                # update stripe customer id
                member_subscription.stripe_customer_id = stripe_customer['id']
                # update stripe card id
                member_subscription.stripe_card_id = stripe_customer['default_source']
                member_subscription.stripe_card_token = stripe_token
                member_subscription.last_invoice_id = latest_invoice_id
                member_subscription.save()
                # return JsonResponse(data=tmp_data, status=status.HTTP_200_OK)
                messages.success(request, 'Credit card updated successfully!')

                return redirect(request.META['HTTP_REFERER'])

            else:
                # no internet connection available
                messages.error(request, 'No internet connection!, try again later')
                return redirect(request.META['HTTP_REFERER'])

        except Exception as ex:
            # rollback if any error occurred
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, "Error occurred when update your credit card!")
            return redirect(request.META['HTTP_REFERER'])


class UpgradeMembershipView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'members_app/profile/account_settings.html'

    def post(self, request, *args, **kwargs):
        try:

            # dict_keys(['csrfmiddlewaretoken', 'upgrade_membership_radio_btn'])
            # save the old values to use them in rollback
            stripe_customer = stripe_subscription = old_stripe_customer = old_stripe_subscription = None
            old_membership = old_subscription = None
            member = request.user
            # cprint(request.POST, "magenta")
            with transaction.atomic():
                # member_subscription_obj = member.member_subscription.get()
                member_subscription_obj = member.subscription.select_for_update().first()
                member_membership = member.subscription.select_for_update().first().stripe_plan_id
                old_subscription = copy.deepcopy(member_subscription_obj)
                old_membership = copy.deepcopy(member_membership)
                # check internet connection
                if check_internet_access() is True:
                    # raise BadRequest
                    new_upgrade_btn = request.POST.get("upgrade_membership_radio_btn")
                    # first, validate the upgrade's inputs
                    if (new_upgrade_btn is None) or (new_upgrade_btn == ''):
                        messages.error(request, 'please select the new upgrade plan!', 'danger')
                        return redirect(request.META.get('HTTP_REFERER'))
                    new_upgrade_plan, new_upgrade_range = request.POST.get("upgrade_membership_radio_btn").split("_")
                    range_label_query = '_yearly' if new_upgrade_range == 'yearly' else "_monthly"
                    range_label_query = new_upgrade_plan + range_label_query
                    # fetch the new membership object
                    new_membership_obj = Membership.objects.select_for_update().filter(
                        Q(slug=range_label_query)).first()

                    # retrieve stripe customer info from stripe
                    stripe_customer = stripe.Customer.retrieve(member_subscription_obj.stripe_customer_id)
                    stripe_subscription = stripe.Subscription.retrieve(member_subscription_obj.stripe_subscription_id)
                    # cprint(stripe_customer, 'green')
                    # cprint(stripe_subscription, 'yellow')
                    old_stripe_customer = copy.deepcopy(stripe_customer)
                    # cprint(stripe_customer.get('subscriptions').get('data')[0].get('id'), 'yellow')
                    # cprint(member_subscription_obj.stripe_subscription_id, 'cyan')

                    # cprint(stripe_subscription.get('items').get('data')[0].id, 'cyan')
                    cprint(new_membership_obj, 'yellow')
                    cprint(new_membership_obj.stripe_price_id, 'magenta')
                    stripe_updated_subscription = stripe.Subscription.modify(
                        member_subscription_obj.stripe_subscription_id,
                        cancel_at_period_end=False,
                        proration_behavior='create_prorations',
                        items=[
                            {
                                'id': stripe_subscription.get('items').get('data')[0].id,
                                "price": new_membership_obj.stripe_price_id
                            },
                        ]
                    )
                    # cprint(stripe_updated_subscription, 'cyan')
                    # # if all validate is ok, upgrade
                    cprint("Stripe updated successfully!", 'green')
                    # update the member's subscription token in predictme db
                    member_subscription_obj.stripe_subscription_id = \
                        stripe_updated_subscription.get('items').get('data')[0].id
                    # cprint("Save the new subscription token to predictme db", 'green')
                    # save the new membership in db
                    member_subscription_obj.stripe_plan_id = new_membership_obj
                    member_subscription_obj.save()
                    # cprint('Save the new membership to predictme db successfully!', 'green')
                    messages.success(request, 'upgrade complete successfully!', 'success')
                    return redirect(request.META.get('HTTP_REFERER'))
                else:
                    # no internet connection
                    messages.error(request, 'No internet connection!, try again later', 'danger')
                    return redirect(request.META.get('HTTP_REFERER'))

        except Exception as ex:
            # rollback if any error occurred
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')
            # start rollback
            old_member = Member.objects.select_for_update().get(pk=member.pk)
            old_member.subscription_set = old_subscription
            old_member.subscription.get().stripe_plan_id = old_membership

            return redirect(request.META.get('HTTP_REFERER'))


class ChargeExtraRecordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            # dict_keys(['csrfmiddlewaretoken', 'upgrade_plan', 'new_upgrade_range'])
            member = request.user
            member_data = get_data_table_overview(member)
            data_handler_obj = member.member_data_file.get()
            all_not_finished_records_count = data_handler_obj.data_sessions_set.filter(is_run_model=False).values_list(
                'all_records_count', flat=True)
            all_not_finished_records_count = sum(list(all_not_finished_records_count))
            member_subscription = member.subscription.get()
            member_data_usage_obj = member.data_usage.filter().first()
            data_usage_rows = int(member_data_usage_obj.records_used)
            membership_obj = member_subscription.stripe_plan_id
            membership_row_count = int(membership_obj.allowed_records_count)
            all_not_finished_records_count = int(data_usage_rows) + int(all_not_finished_records_count)
            # cprint(f"all_not_finished_records_count -> {all_not_finished_records_count}", 'cyan')
            # cprint(f"data_usage_rows-> {data_usage_rows}", 'green')
            subtracted_rows = int(data_usage_rows - membership_row_count)
            new_data_usage_rows = 0  # new rows will updated in data usage table after charging
            stripe_charge = None
            # cprint(request.data, 'cyan')
            # check internet connection
            if check_internet_access() is True:
                """
                {'plan_name': 'Unlimited_development', 'plan_limit': 9999999999, 'current_data_used': 1170, 
                'at_or_below_plan_limit': 9999998829, 'above_plan_rows': 0, 'additional_fee': '$0.00', 
                'total_cost_for_additional': '$0', 'check_records_total': False
                """
                form_data = json.loads(request.data.get("formData"))
                # cprint(form_data, 'cyan')
                stripe_name = form_data.get("name")
                stripe_email = form_data.get("email")
                extra_records = member_data.get("above_plan_rows")
                total_amount = float(member_data.get("total_cost_for_additional").replace("$", ""))
                stripe_token = form_data.get("stripeToken")
                description = "PredictMe Charge"
                # cprint(form_data, 'yellow')
                # check if the numeric inputs are empty or not
                if (extra_records == "") or (form_data.get("totalAmount") == ''):
                    return JsonResponse(data={"msg": "Some data are required!", 'is_done': False}, status=200)

                # validate if the extra rows is more than the allowed or cross the limit
                # cprint(f"extra_records -> {extra_records}", 'cyan')
                # cprint(f"subtracted_rows -> {subtracted_rows}", 'cyan')

                # here if the extra records limited
                if stripe_token is None:
                    # in case the user will use old stripe card, which use it in registration
                    stripe_charge = stripe.Charge.create(
                        amount=int(total_amount * 100),
                        currency="usd",
                        description=description,
                        customer=member_subscription.stripe_customer_id
                    )
                else:
                    # in case the user provide new stripe card
                    stripe_charge = stripe.Charge.create(
                        amount=int(total_amount * 100),
                        currency="usd",
                        source=stripe_token,
                        description=f"Member's email address is: {member.email}, {description}",
                    )

                # check if charge successfully
                if stripe_charge is not None:
                    charge_obj = Charges()
                    charge_obj.member = member
                    charge_obj.charge_token = stripe_charge.get("id")
                    charge_obj.amount = stripe_charge.get('amount')
                    # charge_obj.invoice_token = stripe_charge.get('invoice')
                    charge_obj.status = stripe_charge.get('status')
                    charge_obj.save()

                    # update data usage row for the member
                    new_data_usage_rows = int(int(subtracted_rows) - int(extra_records))
                    member_data_usage_obj.records_used = int(membership_row_count + new_data_usage_rows)
                    member_data_usage_obj.save()
                    return JsonResponse(data={"msg": "Charge Successfully!", "is_done": True}, status=200)

            else:
                # no internet connection
                return JsonResponse(data={"msg": "No internet connection!", 'is_done': False}, status=200)

        except Exception as ex:
            # rollback if any error occurred
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'Error in charge extra records view!!, try again latter')
            return JsonResponse(data={"msg": "Error while charging!!", 'is_done': False}, status=200)


class UpgradeMembershipAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        try:
            new_membership_lbl = ""  # save the label of new membership to return it to frontend with the response
            with transaction.atomic():
                member = request.user
                new_membership_slug = request.data.get("membership_slug")
                member_subscription_obj = member.subscription.select_for_update().get()
                new_membership_obj = Membership.objects.select_for_update().filter(slug=new_membership_slug).first()
                new_membership_lbl = new_membership_obj.get_membership_type_display()

                # fetch stripe customer
                stripe_customer = stripe.Customer.retrieve(member_subscription_obj.stripe_customer_id).to_dict()
                # fetch previous member subscription from stripe
                stripe_old_subscription = stripe.Subscription.retrieve(
                    member_subscription_obj.stripe_subscription_id).to_dict()
                # fetch stripe subscription item
                stripe_subscription_item_id = stripe_old_subscription.get("items").to_dict().get("data")[0].get("id")

                # fetch stripe card details
                stripe_card_obj = stripe.Customer.retrieve_source(stripe_customer.get("id"),
                                                                  stripe_customer.get("default_source")).to_dict()

                # modify the stripe subscription
                stripe_updated_subscription = stripe.Subscription.modify(
                    member_subscription_obj.stripe_subscription_id,
                    billing_cycle_anchor='now',
                    cancel_at_period_end=False,
                    proration_behavior='create_prorations',
                    items=[
                        {
                            'id': stripe_subscription_item_id,
                            "price": new_membership_obj.stripe_price_id,
                        }
                    ]
                )
                cprint('Subscription updated on stripe successfully!', 'green', attrs=['bold'])

                # update the membership for the member
                member_subscription_obj.membership = new_membership_obj

                # update stripe new value in subscription table
                member_subscription_obj.stripe_subscription_id = stripe_updated_subscription.get("id")
                start_date = datetime.fromtimestamp(stripe_updated_subscription.get("current_period_start"),
                                                    tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                end_date = datetime.fromtimestamp(stripe_updated_subscription.get("current_period_end"),
                                                  tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                member_subscription_obj.subscription_status = True if stripe_updated_subscription.get(
                    "status") == "active" else False
                member_subscription_obj.subscription_period_start = start_date
                member_subscription_obj.subscription_period_end = end_date
                member_subscription_obj.card_expire = datetime(stripe_card_obj.get("exp_year"),
                                                               stripe_card_obj.get("exp_month"), 1)
                member_subscription_obj.last_invoice_id = stripe_updated_subscription.get("latest_invoice")
                member_subscription_obj.save()
                cprint('Membership & Subscription updated on our db successfully!', 'green', attrs=['bold'])

                messages.success(request, f"Your membership upgraded to {new_membership_lbl} successfully!")

            # raise AttributeError("Custom Assertion!")
            return JsonResponse(
                data={"msg": f"Your membership upgraded successfully to {new_membership_lbl}", "is_error": False},
                status=status.HTTP_200_OK)
        except Exception as ex:
            # rollback if any error occurred
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return JsonResponse(data={"msg": "Error when upgrade membership!", 'is_error': True},
                                status=status.HTTP_200_OK)


class ChangeStripeCardView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            cprint(request.POST, 'yellow')
            return redirect(request.META.get('HTTP_REFERER'))
        except Exception as ex:
            # rollback if any error occurred
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')
            return JsonResponse(data={"msg": "Error while charging!!", 'is_done': False}, status=200)


class RegisterSuccessfully(TemplateView):
    template_name = "membership/inc/payment_success.html"
