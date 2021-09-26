from django import forms
from django_countries.fields import CountryField
from django.core import validators
from django.forms.models import model_to_dict
import re
from .models import CompanySettings
from django.db import connection
from termcolor import cprint

# company_data = {
#     "description": "description",
#     "keywords": "keywords",
#     "close_msg": "Close Message"
# }

company_data = CompanySettings.objects.filter(slug='company').first()
if company_data is not None:
    company_data = model_to_dict(company_data)
else:
    company_data = {
        "description": "description",
        "keywords": "keywords",
        "close_msg": "Close Message"
    }

REGEX_PATTERS = {
    "NAME": re.compile(r"^[a-zA-Z '.-]*$", re.IGNORECASE),  # name or first second
    "PHONE": re.compile(r"([+]?\d{1,2}[.\s]?)?(\d{3}[.-]?){2}\d{4}"),  # phone with country code
}


class CompanySettingsForm(forms.Form):
    name = forms.CharField(label="Website Name", max_length=20, required=False, validators=[
        validators.RegexValidator(regex=REGEX_PATTERS['NAME'], message="Name must be Alphabet!")])
    email = forms.EmailField(label="Email Address", max_length=100, required=False,
                             validators=[validators.EmailValidator(message="Email Not Valid!")])
    phone = forms.CharField(label="Contact Phone", max_length=50, required=False, validators=[
        validators.RegexValidator(regex=REGEX_PATTERS['PHONE'], message="Phone number not correct!")])
    logo = forms.FileField(label='Logo', required=False)
    url = forms.URLField(label="Website URL", required=False, max_length=100,
                         validators=[validators.URLValidator(message="Website URL not correct!")])
    description = forms.CharField(label="Description", required=False, widget=forms.Textarea,
                                  initial=company_data.get('description'))
    keywords = forms.CharField(label="Keywords", required=False, widget=forms.Textarea,
                               initial=company_data.get('keywords'))
    country = CountryField(blank_label='Select Country').formfield(label="Country", required=False)
    city = forms.CharField(label="City", max_length=20, required=False, validators=[
        validators.RegexValidator(regex=REGEX_PATTERS['NAME'], message="City must be Alphabet!")])
    admin_name = forms.CharField(label="Admin Name", max_length=20, required=False, validators=[
        validators.RegexValidator(regex=REGEX_PATTERS['NAME'], message="Admin Name must be Alphabet!")])
    admin_email = forms.EmailField(label="Admin Email", max_length=100, required=False,
                                   validators=[validators.EmailValidator(message="Admin Email Not Valid!")])
    status = forms.BooleanField(label="Website in Maintenance mode:", required=False)
    closed_msg = forms.CharField(label="Closed Message", required=False, widget=forms.Textarea,
                                 initial=company_data.get('close_msg'))
