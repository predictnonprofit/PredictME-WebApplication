import json
import traceback
from django.core.exceptions import BadRequest
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import (render, redirect, reverse, HttpResponse)
from django.views.generic import TemplateView, View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from predict_me.my_logger import log_exception
from users.models import Member
from .models import (Subscription, Membership, Charges)
from termcolor import cprint
from prettyprinter import pprint
import stripe
import os
import datetime
import pytz
from django.db.models import Q
from django.db import transaction
from predict_me.helpers import check_internet_access
import copy

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class CheckoutView(View):
    template_name = "membership/checkout.html"

    def get(self, request):
        stripe_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        subscription = Subscription.objects.get(member_id=request.user)
        return render(request, "membership/checkout.html",
                      context={"subscription": subscription, "stripe_key": stripe_key})

    def post(self, request):
        if request.method == "POST":
            # check if there is any internet connection errors
            if check_internet_access() is True:
                # internet connection available
                member = request.user
                # cprint(request.POST, "cyan")
                sub_range = request.POST.get("sub_range")
                payment_agree = request.POST.get("agree_payment")
                stripe_token = request.POST.get("stripeToken")
                member.stripe_card_token = stripe_token
                member.status = "active"
                member.save()
                # id, created, plan[interval], plan[product], price[active], latest_invoice, status, current_period_end
                # current_period_start, customer
                subscription = Subscription.objects.get(member_id=member)
                # cprint(subscription.stripe_plan_id, 'blue')
                membership = Membership.objects.filter(
                    Q(range_label=sub_range) & Q(parent=subscription.stripe_plan_id.slug)).first()
                cprint("Here membership view: ", 'red')
                cprint(membership, "yellow")
                subscription.stripe_plan_id = membership
                subscription.save()
                # cprint(subscription.stripe_plan_id, 'magenta')
                customer = stripe.Customer.modify(
                    subscription.member_id.stripe_customer_id,
                    card=stripe_token
                )
                member.stripe_customer_id = customer['id']
                member.save()
                stripe_subscription_obj = stripe.Subscription.create(
                    customer=customer['id'],
                    items=[
                        {"price": subscription.stripe_plan_id.stripe_price_id},
                    ],
                )
                tmp_customer = stripe.Customer.retrieve(customer['id'])
                card_id = tmp_customer['default_source']
                subscription.stripe_subscription_id = stripe_subscription_obj['id']
                subscription.stripe_card_id = card_id
                card_obj = stripe.Customer.retrieve_source(customer['id'], card_id)
                start_date = datetime.datetime.fromtimestamp(stripe_subscription_obj['current_period_start'],
                                                             tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                end_date = datetime.datetime.fromtimestamp(stripe_subscription_obj['current_period_end'],
                                                           tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                subscription.subscription_status = True if stripe_subscription_obj['status'] == "active" else False
                subscription.subscription_period_start = start_date
                subscription.subscription_period_end = end_date
                subscription.card_expire = datetime.datetime(card_obj['exp_year'], card_obj['exp_month'], 1)
                subscription.sub_range = sub_range

                subscription.save()

                return redirect(reverse("register_successfully"))
            else:
                # no internet connection avaliable
                messages.error(request, "No Internet Connection!, try again later.", 'danger')
                return redirect(reverse("register_successfully"))


class UpdateStripeView(LoginRequiredMixin, TemplateView):
    login_url = "login"
    template_name = 'members_app/profile/account_settings.html'

    def get(self, request, *args, **kwargs):
        return redirect("profile-account-settings")

    def post(self, request, *args, **kwargs):
        try:
            # <QueryDict: {'csrfmiddlewaretoken': ['my12gzlhkhPiFjbik3Z5ekH5S3s0fGJycRF5UAh6HNYoapV7f5lvSUXhMgnJoFIl'],
            # 'form-name': ['stripe-form'], 'full_name': ['Avye Abbott'], 'sub_range': ['yearly'],
            # 'stripeToken': ['tok_1IeHTtCXFX3jJJ8Kycjk1WHo'], 'upgrade_plane': ['professional'],
            # 'professionalRange': ['yearly']}>
            cprint(request.POST.keys(), 'yellow')
            cprint(request.POST, 'blue')

            # check internet connection available
            if check_internet_access() is True:
                member = Member.objects.get(email=request.user.email)
                member_subscription = member.member_subscription.get()
                member_subscription_backup = copy.deepcopy(member_subscription)
                opposite_label = ''
                sub_range = request.POST.get("sub_range")
                stripe_token = request.POST.get("stripeToken")
                # cprint(membership.range_label, 'magenta')
                # print(sub_range, "==>", member_subscription.stripe_plan_id.parent)
                # print("Range =>", membership.range_label)
                if sub_range != member_subscription.sub_range:
                    if sub_range == 'monthly':
                        opposite_label = "yearly"
                    else:
                        opposite_label = 'monthly'
                    new_membership = Membership.objects.filter(
                        Q(range_label=sub_range) & Q(parent=member_subscription.stripe_plan_id.parent)).first()
                    member_subscription.stripe_plan_id = new_membership
                    member_subscription.save()
                    stripe_customer = stripe.Customer.modify(
                        member_subscription.member_id.stripe_customer_id,
                        card=stripe_token
                    )
                    cprint('stripe_customer ok', 'green')
                    # update stripe customer id
                    member.stripe_customer_id = stripe_customer['id']
                    # update stripe card id
                    member.stripe_card_token = stripe_token
                    member.save()
                    # get stripe card token
                    card_id = stripe_customer['default_source']
                    fetch_subscription = stripe.Subscription.retrieve(member_subscription.stripe_subscription_id)
                    stripe_subscription = stripe.Subscription.modify(
                        member_subscription.stripe_subscription_id,
                        billing_cycle_anchor='now',
                        cancel_at_period_end=False,
                        proration_behavior='create_prorations',
                        items=[
                            {
                                'id': fetch_subscription['items']['data'][0].id,
                                "price": member_subscription.stripe_plan_id.stripe_price_id,
                            }
                        ]
                    )
                    cprint('stripe subscription ok!', 'cyan')
                    # update stripe new value in subscription table
                    member_subscription.stripe_subscription_id = stripe_subscription['id']
                    member_subscription.stripe_card_id = card_id
                    card_obj = stripe.Customer.retrieve_source(stripe_customer['id'], card_id)
                    start_date = datetime.datetime.fromtimestamp(stripe_subscription['current_period_start'],
                                                                 tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                    end_date = datetime.datetime.fromtimestamp(stripe_subscription['current_period_end'],
                                                               tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
                    member_subscription.subscription_status = True if stripe_subscription[
                                                                          'status'] == "active" else False
                    member_subscription.subscription_period_start = start_date
                    member_subscription.subscription_period_end = end_date
                    member_subscription.card_expire = datetime.datetime(card_obj['exp_year'], card_obj['exp_month'], 1)
                    member_subscription.sub_range = sub_range
                    member_subscription.last_invoice_id = stripe_subscription['latest_invoice']
                    member_subscription.save()
                    messages.success(request, 'Subscription data updated successfully!', 'success')

                # check if the subscription range is changed

                return redirect('profile-account-settings')

            else:
                # no internet connection available
                messages.error(request, 'No internet connection!, try again later', 'danger')
                return redirect('profile-account-settings')

        except Exception as ex:
            # rollback if any error occurred
            # cprint(traceback.format_exc(), 'red')
            cprint("Error occurred when update stripe membership!", 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is error!, try again latter')


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
                member_subscription_obj = member.member_subscription.select_for_update().first()
                member_membership = member.member_subscription.select_for_update().first().stripe_plan_id
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
            old_member.member_subscription_set = old_subscription
            old_member.member_subscription.get().stripe_plan_id = old_membership

            return redirect(request.META.get('HTTP_REFERER'))


class ChargeExtraRecordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            # dict_keys(['csrfmiddlewaretoken', 'upgrade_plan', 'new_upgrade_range'])
            member = request.user
            data_handler_obj = member.member_data_file.get()
            all_not_finished_records_count = data_handler_obj.data_sessions_set.filter(is_run_model=False).values_list(
                'all_records_count', flat=True)
            all_not_finished_records_count = sum(list(all_not_finished_records_count))
            member_subscription = member.member_subscription.get()
            member_data_usage_obj = member.data_usage.filter().first()
            data_usage_rows = int(member_data_usage_obj.records_used)
            membership_obj = member_subscription.stripe_plan_id
            membership_row_count = int(membership_obj.allowed_records_count)
            all_not_finished_records_count = int(data_usage_rows) + int(all_not_finished_records_count)
            cprint(f"all_not_finished_records_count -> {all_not_finished_records_count}", 'cyan')
            # cprint(f"data_usage_rows-> {data_usage_rows}", 'green')
            subtracted_rows = int(data_usage_rows - membership_row_count)
            new_data_usage_rows = 0  # new rows will updated in data usage table after charging
            stripe_charge = None
            # cprint(request.data, 'cyan')
            # check internet connection
            if check_internet_access() is True:
                form_data = json.loads(request.data.get("formData"))
                stripe_name = form_data.get("name")
                stripe_email = form_data.get("email")
                extra_records = form_data.get("extraRows")
                total_amount = float(form_data.get("totalAmount"))
                stripe_token = form_data.get("stripeToken")
                description = "PredictMe Charge"
                # cprint(form_data, 'yellow')
                # check if the numeric inputs are empty or not
                if (extra_records == "") or (form_data.get("totalAmount") == ''):
                    return JsonResponse(data={"msg": "Some data are required!", 'is_done': False}, status=200)

                # validate if the extra rows is more than the allowed or cross the limit
                cprint(f"extra_records -> {extra_records}", 'cyan')
                cprint(f"subtracted_rows -> {subtracted_rows}", 'cyan')
                if int(extra_records) > all_not_finished_records_count:
                    return JsonResponse(data={"msg": "Total records is more than allowed!!", 'is_done': False},
                                        status=200)
                else:
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
            messages.error(request, 'There is errors!, try again latter')
            return JsonResponse(data={"msg": "Error while charging!!", 'is_done': False}, status=200)


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
