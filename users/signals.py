import traceback

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.db import transaction
from termcolor import cprint

from data_handler.models import (DataFile)
from membership.models import (Subscription)
from predict_me.my_logger import log_exception

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_subscription_datafile_object_for_member(sender, instance, created, **kwargs):
    """
    this function will run after new member register, to create subscription for members
    object to the new member,
    Arguments:
        sender {[type]} -- [description]
        instance {[type]} -- [description]
        created {[type]} -- [description]
    """
    try:
        # print(sender, instance, created, kwargs)
        if created:
            with transaction.atomic():
                stripe_metadata = {}
                stripe_description = ""
                # check if it is in debug mode
                if settings.DEBUG is True:
                    # metadata["user_type"] = "development"
                    stripe_metadata.update({"user_type": "development"})
                    stripe_description = f"{instance.full_name} :-> Test Customer"
                else:
                    stripe_metadata.update({"user_type": "production"})
                    stripe_description = f"{instance.full_name} :-> Production Customer"

                subscription_obj, created = Subscription.objects.get_or_create(member=instance)
                # check if the new member has stripe id
                if (subscription_obj.membership is None) or (subscription_obj.membership == ""):
                    new_member_id = stripe.Customer.create(email=instance.email, name=instance.full_name,
                                                           description=stripe_description, metadata=stripe_metadata)
                    subscription_obj.stripe_customer_id = new_member_id['id']
                    # create data file object for the new member
                    data_file = DataFile()
                    data_file.member = instance
                    data_file.file_upload_procedure = None
                    data_file.data_file_path = None
                    data_file.save()
                    subscription_obj.save()

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())
    else:
        if created:
            cprint(f"subscription and data file object for member {instance.email} created successfully", 'green',
                   'on_grey', attrs=['bold'])


post_save.connect(create_subscription_datafile_object_for_member, sender=get_user_model())
