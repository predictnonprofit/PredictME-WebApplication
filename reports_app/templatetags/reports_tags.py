from django import template

register = template.Library()


@register.filter
def get_var_type(value):
    return type(value)


@register.filter
def slice_url_path(url):
    last_url_param = url.split("/")[-1]
    return last_url_param
