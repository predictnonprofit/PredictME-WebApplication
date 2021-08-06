from django import template
from django.urls import resolve
from termcolor import cprint
import re

register = template.Library()


@register.filter
def sub_records(all_recs, allowed_recs):
    if all_recs and allowed_recs:
        return all_recs - allowed_recs


@register.filter
def extra_fee_records(records_total):
    if records_total:
        return float(records_total * 0.50)


@register.filter
def get_type(value):
    return type(value).__name__.strip()


@register.filter
def extract_first_value_from_iterator(value):
    first_value = '(Not Ready Yet)'
    # check if the value is None or not
    if value is not None:
        if (type(value).__name__ == 'list') or type(value).__name__ == 'tuple':
            first_value = value[0]
        else:
            first_value = 0

    return first_value


@register.filter
def get_how_many_left(value):
    try:
        left_value = None
        value = int(value)
        left_value = 100 - value
        return left_value
    except TypeError:
        return 0


@register.filter
def get_model_name_dashboard(value):
    # check the type of value
    if type(value).__name__ == 'list':
        return ". ".join(value)
    
    return value


@register.filter
def get_cols(value):
    # cprint(value, 'green')
    return 0


@register.filter
def clean_categorical_btn(value):
    pattern = r"^[a-z]."
    new_value = re.sub(pattern, "", value, flags=re.I)
    return new_value


@register.filter
def get_donor_predicted(value: str):
    value = value.strip()
    return value.split(" ")[0]


@register.filter
def get_url_name(url_path):
    return resolve(url_path).url_name


@register.filter
def check_member_if_run_completed_sessions(member):
    pass
