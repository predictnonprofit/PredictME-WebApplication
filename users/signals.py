from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.contrib.auth import get_user_model
from membership.models import (Subscription)
from data_handler.models import (DataFile, DataHandlerSession)
import stripe
import os
from termcolor import cprint
from django.conf import settings
from prettyprinter import pprint
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_usermembership_memberdatafile(sender, instance, created, **kwargs):
    """
    this function will run after new member register, to create usermembership
    object to the new member,
    Arguments:
        sender {[type]} -- [description]
        instance {[type]} -- [description]
        created {[type]} -- [description]
    """
    try:
        # print(sender, instance, created, kwargs)
        if created:
            subscription_obj, created = Subscription.objects.get_or_create(member_id=instance)
            # cprint(subscription_obj, "yellow")
            # check if the new member has stripe id
            if subscription_obj.stripe_plan_id is None or subscription_obj.stripe_plan_id == "":
                # member = instance
                new_member_id = stripe.Customer.create(email=instance.email, name=instance.full_name)
                # subscription = stripe.Subscription.create(
                #     customer=new_member_id['id'],
                #     items=[
                #         {"price": "price_1HW4LjCXFX3jJJ8K8pzAc8uu"},
                #     ],
                # )
                # pprint(new_member_id)
                subscription_obj.stripe_customer_id = new_member_id['id']
                instance.stripe_customer_id = new_member_id['id']
                instance.save()
                # create data file object for the new member
                data_file = DataFile()
                data_file.member = instance
                data_file.file_upload_procedure = None
                data_file.data_file_path = None
                data_file.save()
                # subscription_obj.data_file_obj = data_file
                subscription_obj.save()

            # data_file_obj, created = DataFile.objects.get_or_create(member=user_membership_obj)
            # data_file_obj.save()

    except ObjectDoesNotExist as ex:

        return HttpResponseNotFound("Oops! Member Not found!")
    else:
        if created:
            print("members data file, usermembership are created successfully!")


post_save.connect(create_usermembership_memberdatafile, sender=get_user_model())
