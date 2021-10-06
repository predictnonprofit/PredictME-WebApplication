# -*- coding: utf-8 -*-#
import traceback

import stripe
from prettyprinter import cpprint
from termcolor import cprint

from predict_me.helpers import check_internet_access
from predict_me.my_logger import log_exception


class PredictMEStripeProcesses:
    def __init__(self, member_subscription_obj):
        self.member_subscription_obj = member_subscription_obj
        self.stripe_customer_id = self.member_subscription_obj.stripe_customer_id
        self.stripe_card_id = self.member_subscription_obj.stripe_card_id

    def stripe_retrieve_customer_source_to_cache(self):
        stripe_data = {}  # dict to hold all stripe retrieved data
        try:
            if check_internet_access():
                stripe_card_obj = stripe.Customer.retrieve_source(
                    self.member_subscription_obj.stripe_customer_id,
                    self.member_subscription_obj.stripe_card_id,
                )
                # check if the user has data on stripe, to avoid any error in registration process
                if stripe_card_obj:
                    stripe_data['last4'] = stripe_card_obj.get("last4")
                    stripe_customer = self.stripe_retrieve_customer()
                    stripe_data['s_name'] = stripe_customer.get('name')  # enable this
                    # stripe_data['subscription_id'] = stripe_customer.get('subscriptions').get('data')[0].get('id')
                    stripe_data['s_email'] = stripe_customer.get('email')
                    stripe_data['status'] = stripe_customer.get('subscriptions').get('data')[0].get('status')
                    stripe_data['current_period_start'] = stripe_customer.get('subscriptions').get('data')[0].get(
                        'current_period_start')
                    stripe_data['current_period_end'] = stripe_customer.get('subscriptions').get('data')[0].get(
                        'current_period_end')

                return stripe_data

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_data

    def stripe_update_customer_source(self, stripe_token, stripe_name=None):
        stripe_updated_data = None
        try:
            cpprint(locals(), end="\n")
            # validate the stripe token if empty
            if stripe_token == "" or stripe_token is None:
                raise Exception("PMException, Stripe Token Required!")

            # new_updated_data = {
            #     "source": stripe_token,
            # }
            new_updated_data = {
                "card": stripe_token,
            }
            # check if the name passed
            if stripe_name is not None:
                new_updated_data.update({
                    "name": stripe_name
                })
            if check_internet_access():
                stripe_updated_data = stripe.Customer.modify(
                    self.member_subscription_obj.stripe_customer_id,
                    **new_updated_data
                )
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_updated_data

    def stripe_charge_customer(self, total_amount, description):
        stripe_charged_data = None
        try:
            if check_internet_access():
                stripe_charged_data = stripe.PaymentIntent.create(
                    amount=total_amount,
                    currency='usd',
                    customer=self.member_subscription_obj.stripe_customer_id,
                    payment_method=self.member_subscription_obj.stripe_card_id,
                    off_session=True,
                    confirm=True,
                    description=description
                )
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_charged_data

    def stripe_retrieve_customer(self, custom_customer_token=None):
        stripe_data = None
        try:
            customer_token = None
            # check if it will custom customer
            if custom_customer_token is not None:
                customer_token = custom_customer_token
            else:
                customer_token = self.stripe_customer_id
            if check_internet_access() is True:
                stripe_data = stripe.Customer.retrieve(customer_token)
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_data

    def stripe_retrieve_subscription(self):
        stripe_data = None
        try:
            if check_internet_access():
                stripe_data = stripe.Subscription.retrieve(self.member_subscription_obj.stripe_subscription_id)
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_data

    def stripe_retrieve_card(self, custom_customer_token=None, custom_card_token=None):
        stripe_data = None
        try:
            customer_token = None
            card_token = None
            # check if it will custom customer and custom card
            if custom_customer_token is not None and custom_card_token is not None:
                customer_token = custom_customer_token
                card_token = custom_card_token
            else:
                customer_token = self.stripe_customer_id
                card_token = self.stripe_card_id
            if check_internet_access() is True:
                stripe_data = stripe.Customer.retrieve_source(customer_token, card_token)
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_data

    def stripe_update_subscription(self, subscription_token, stripe_new_price_token):
        stripe_data = None
        try:
            if check_internet_access():
                stripe_data = stripe.Subscription.modify(
                    self.member_subscription_obj.stripe_subscription_id,
                    cancel_at_period_end=False,
                    proration_behavior='create_prorations',
                    items=[
                        {
                            'id': subscription_token,
                            "price": stripe_new_price_token
                        },
                    ]
                )
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_data

    def stripe_create_subscription(self, stripe_price_token):
        stripe_data = None
        try:
            # check if stripe price token not empty
            if stripe_price_token == "" or stripe_price_token is None:
                raise Exception("PMException Stripe Price Token Required!!!")
            if check_internet_access() is True:
                stripe_data = stripe.Subscription.create(
                    customer=self.stripe_customer_id,
                    items=[
                        {"price": stripe_price_token},
                    ],
                )
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_data

    def stripe_retrieve_invoices(self, start_time, end_time, customer_stripe_token=None):
        stripe_data = None
        try:
            customer_token = None
            # check if stripe price token not empty
            if customer_stripe_token == "" or customer_stripe_token is None:
                customer_token = self.stripe_customer_id
            else:
                customer_token = customer_stripe_token
            if check_internet_access() is True:
                stripe_data = stripe.Invoice.list(customer=customer_token, created={
                    'gte': int(start_time),
                    "lte": int(end_time)
                })
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_data

    def stripe_retrieve_transactions(self, customer_stripe_token=None):
        stripe_data = None
        try:
            customer_token = None
            # check if stripe price token not empty
            if customer_stripe_token == "" or customer_stripe_token is None:
                customer_token = self.stripe_customer_id
            else:
                customer_token = customer_stripe_token
            if check_internet_access() is True:
                stripe_data = stripe.Charge.list(customer=customer_token)
            else:
                raise Exception("No Internet Connection")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return stripe_data
