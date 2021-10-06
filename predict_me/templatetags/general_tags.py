import ast
from django import template

register = template.Library()


@register.filter
def get_type(value):
    return type(value).__name__.strip()


@register.simple_tag
def create_dict_from_string(txt):
    return ast.literal_eval(txt)
