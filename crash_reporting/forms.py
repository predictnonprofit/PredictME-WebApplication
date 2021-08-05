# -*- coding: utf-8 -*-#

from django.core import validators
from django.forms import ModelForm
import traceback

from predict_me.my_logger import log_exception
from .models import CrashReport
from termcolor import cprint
from django.utils.crypto import get_random_string
import string

alphabet = string.ascii_letters + string.digits


class CrashReportForm(ModelForm):
    class Meta:
        model = CrashReport
        exclude = ('member', 'is_seen', 'is_solved', 'crash_status')
        labels = {
            'file_attachment': 'Attachment',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(CrashReportForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        try:
            model = super(CrashReportForm, self).save(commit=False)
            # set the user
            model.member = self.request.user
            # check if there files uploaded
            if model.file_attachment.name is not None:
                random_file_attachment_name = get_random_string(10, alphabet)
                random_file_attachment_name = random_file_attachment_name + "_" + model.file_attachment.name
                model.file_attachment.name = random_file_attachment_name

            if model.screenshot.name is not None:
                random_screenshot_name = get_random_string(10, alphabet)
                random_screenshot_name = random_screenshot_name + "_" + model.screenshot.name
                model.screenshot.name = random_screenshot_name

            if commit:
                model.save()
            return model
        except Exception as ex:
            log_exception(traceback.format_exc())
            cprint(traceback.format_exc(), "red")
