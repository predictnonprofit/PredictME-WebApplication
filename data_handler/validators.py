# this file contain class which will validate the user data file rows
import string
from itertools import cycle
import pandas as pd
import numpy as np
from collections import namedtuple
from rest_framework.response import Response
from termcolor import cprint
import re
import traceback
from predict_me.my_logger import log_exception

# pd.set_option('precision', 0)
pd.options.display.float_format = '${:,.0f}'.format

DataStatus = namedtuple("DataStatus", ["status", "value"])


class DataValidator:
    def __init__(self):
        # self.data = data
        self.value_dict = {}

        # call this method will call the validation steps

    def detect_and_validate(self, val="", dtype=None, original_dtype=None):
        """
        this method will call all validation methods in this class
        Returns:

        """
        # [unique identifier (id), textual field, numeric field, donation field]
        try:
            the_value = val
            if "unique identifier" in dtype:
                san = self.sanitize_numeric_data(the_value, 'unique_id')
            elif "text field" in dtype:
                san = self.sanitize_numeric_data(the_value, 'text')
            elif "numeric field" in dtype:
                san = self.sanitize_numeric_data(the_value, 'numeric')
            elif "donation field" in dtype:
                san = self.sanitize_numeric_data(the_value, 'donation')
            elif "geo-location" in dtype:
                san = self.sanitize_numeric_data(the_value, 'text')

            if san.status:
                # check if the value contain any error or not valid data
                the_validate_dict_values = self.return_the_error_msg(True, san.value, "data not valid",
                                                                     data_type=f"{dtype}", org_dtype=original_dtype)
                # cprint(the_validate_dict_values, 'blue')
            else:
                the_validate_dict_values = self.return_the_error_msg(False, san.value, "valid data",
                                                                     data_type=f"{dtype}", org_dtype=original_dtype)
            # print(the_validate_dict_values)
            # print(dtype)
            return the_validate_dict_values

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(traceback.format_exc())

    def sanitize_numeric_data(self, data_value, dtype=None):
        try:
            sanitized = str(data_value)
            data_value = str(data_value)
            results = DataStatus(status=False, value=data_value)  # return if data is validate, and the sanitized value
            bad_strings = [
                ';', '$', '&&', '../', '<', '>', '%3C', '%3E', '\'', '--', '1,2', '\x00',
                '`', '(', ')', '&', "%", "!", "+", "=", "^", "_", "-", "#", "@", "*", 'file://', 'input://'
            ]
            all_punctuations = list(string.punctuation) + bad_strings
            bad_strings = set(all_punctuations)
            all_ascii_letters = list(string.ascii_letters)
            # check what is the dtype and implement the required conditions
            if dtype == "donation":

                if data_value.isdigit():
                    results = DataStatus(status=False, value=data_value)
                else:
                    if data_value == "" or data_value is None or data_value.lower() == "nan":

                        # check if the number is empty
                        results = DataStatus(status=True, value=data_value)
                    else:
                        # here if the number not empty
                        for bad_str, asciistr in zip(cycle(bad_strings), all_ascii_letters):
                            # if bad_str in sanitized and bad_str != ".":  # check if string contains punctuations
                            if bad_str in sanitized:  # check if string contains punctuations
                                sanitized = sanitized.replace(bad_str, '')
                                results = DataStatus(status=True, value=sanitized)

                            if asciistr in sanitized:  # check if string contains letters
                                sanitized = sanitized.replace(asciistr, '')
                        if len(sanitized) > 0:
                            results = DataStatus(status=False, value=sanitized)
                        else:
                            results = DataStatus(status=True, value=sanitized)

            elif dtype == "numeric":
                if data_value == "" or data_value is None or data_value.lower() == "nan":
                    # check if the number is empty
                    results = DataStatus(status=True, value=sanitized)
                else:
                    # regex = r"(?<!\.)\b[0-9]+\b(?!\.)"
                    regex = r"^ *[0-9][0-9 ]*$"
                    pattern = re.compile(regex, flags=re.IGNORECASE | re.MULTILINE)
                    match = pattern.search(data_value)
                    # print(data_value.isdigit())

                    if not match:
                        results = DataStatus(status=True, value=data_value)
                    else:
                        results = DataStatus(status=False, value=data_value)

            elif dtype == "text":
                results = DataStatus(status=False, value=data_value)
                # print(f"data value =--> {data_value}  <=====> sanitized --> {sanitized}")

            elif dtype == "unique_id":
                results = DataStatus(status=False, value=data_value)

            return results
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(traceback.format_exc())

    def validate_empty(self, value):
        try:
            tmp_val = value
            if tmp_val == "" or tmp_val is None or tmp_val == "nan" or tmp_val == "Nan":
                return True
            else:
                return False
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(traceback.format_exc())

    def return_the_error_msg(self, is_error: bool, val: str, msg="", data_type="", org_dtype=""):
        try:
            dtype_dict = {"int64": "Numeric", 'object': "Text", "bool": "Text", "float64": 'Numeric'}
            val = val.strip() or val
            if msg and data_type and org_dtype:
                return {"is_error": is_error, "value": val, "msg": msg, "data_type": data_type,
                        "original_dtype": dtype_dict.get(org_dtype, "Unknown Dtype!")}
            else:
                return {"is_error": is_error, "value": val, "data_type": data_type,
                        "original_dtype": dtype_dict.get(org_dtype, "Unknown Dtype!")}

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(traceback.format_exc())


class CheckInDataError(Exception):
    """Exception raised for errors in the columns pick dialog,
    it return Response

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        cprint(f'Error Message: -> {self.message}', 'red')
        return Response(f"{self.message}", status=401)
