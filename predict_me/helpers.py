import traceback
from ast import literal_eval
import requests
from termcolor import cprint

from predict_me.my_logger import log_exception


def check_internet_access():
    url = 'http://clients3.google.com/generate_204'

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 204:
            # print(response.status_code)
            # print(response.ok)
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
