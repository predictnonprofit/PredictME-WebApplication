# -*- coding: utf-8 -*-#
from django.forms import ModelForm
from .models import MemberMessages


class MemberMessagesForm(ModelForm):
    class Meta:
        model = MemberMessages
        fields = ('sender', 'subject', "other_subject", "attachment", 'message')

