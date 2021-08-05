from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from termcolor import cprint
from data_handler.models import (DataFile, DataHandlerSession)

import os


def create_datahandler_session(sender, instance, created, **kwargs):
    """
    this function will run after new member register, to create usermembership
    object to the new member,
    Arguments:
        sender {[type]} -- [description]
        instance {[type]} -- [description]
        created {[type]} -- [description]
    """
    try:

        if created:
            print(sender, instance, created, kwargs)
            DataHandlerSession.objects.get_or_create(data_handler_id=instance)
            data_handler_session, created = DataHandlerSession.objects.get_or_create(data_handler_id=instance)
            data_handler_session.save()
    except ObjectDoesNotExist as ex:

        return HttpResponseNotFound("Oops! Data handler session Not found!")
    else:
        # this for try
        if created:
            print("Data handler sessions created")


post_save.connect(create_datahandler_session, sender=DataFile)
