import traceback
from ast import literal_eval

import requests
from prettyprinter import (cpprint)
from termcolor import cprint

from predict_me.my_logger import log_exception


def check_internet_access():
    url = 'http://clients3.google.com/generate_204'

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 204:
            # print(response.status_code)
            response.raise_for_status()
            return True
    except requests.exceptions.RequestException as err:
        # cprint(traceback.format_exc(), 'red')
        cprint("Something Else Error!!!", "red")
        log_exception("OOps: Something Else:-> " + traceback.format_exc())
        return False
    except requests.exceptions.HTTPError as errh:
        # cprint(traceback.format_exc(), 'red')
        cprint("Http Error!!!", 'red')
        log_exception("Http Error:-> " + traceback.format_exc())
        return False
    except requests.exceptions.ConnectionError as errc:
        # cprint(traceback.format_exc(), 'red')
        cprint("Error Connecting!!!", 'red')
        log_exception("Error Connecting::-> " + traceback.format_exc())
        return False
    except requests.exceptions.Timeout as errt:
        # cprint(traceback.format_exc(), 'red')
        cprint("Timeout Error!!!", 'red')
        log_exception('Timeout Error:-> ' + traceback.format_exc())
        return False


def is_integer_or_float(value):
    """
    This function will determine the type of value and return int or float
    """
    try:

        val = literal_eval(value)

        if isinstance(val, int):
            # cprint("Integer value", 'green')
            return int(val)
        elif isinstance(val, float):
            # cprint("float value", 'yellow')
            return float(val)

    except (TypeError, ValueError):
        return False


def quick_print(obj):
    cprint("Call quick_print function:-> ", 'green', attrs=['bold'])
    output = []
    for ob in dir(obj):
        if not ob.startswith('__'):
            output.append(ob)
    output = sorted(output)
    cpprint(output)

# def set_permissions_and_groups_to_members():
#     """
#     just for developments
#     """
#     try:
#         all_groups = Group.objects.all()
#         all_permissions = Permission.objects.all()
#         all_members = Member.objects.all()
#
#         for member in all_members:
#             # check if the member is administrator account
#             if member.is_superuser and member.is_staff:
#                 administrator_group = Group.objects.filter(name='Administrator').first()
#                 is_in_groups = member.groups.filter(name='Administrator').exists()
#                 # check if administrator group exists in the member
#                 if not is_in_groups:
#                     member.groups.add(administrator_group)
#                     member.save()
#             else:
#                 data_handler_groups = Group.objects.filter(
#                     name__in=['Data Handler', 'Data Handler Session', 'Data Handler Usage',
#                               'Data Handler Download Counter',
#                               "Data Handler Run History"])
#                 # cprint(f"Before:->  {member.groups.all()}", 'yellow')
#                 for group in data_handler_groups:
#                     is_in_group = member.groups.filter(name=group.name).exists()
#                     if not is_in_groups:
#                         member.groups.add(group)
#                         member.save()
#                 # cprint(f"After:->  {member.groups.all()}", 'green')
#                 print('')
#     except Exception as ex:
#         cprint(traceback.format_exc(), 'red')
#         log_exception(traceback.format_exc())
