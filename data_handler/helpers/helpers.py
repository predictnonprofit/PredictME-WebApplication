from pathlib import Path
import os
from datetime import date

import pandas as pd
from django.http import HttpResponse
from prettyprinter import pprint, cpprint
from seaborn.external.docscrape import header
from django.conf import settings
from data_handler.models import (DataFile, DataHandlerSession, RunHistory)
from users.models import Member
from data_handler.validators import *
from itertools import islice
from termcolor import cprint
import traceback
from predict_me.my_logger import (log_exception, log_info)
from predict_me.constants.countries import *
import re
from django.apps import apps
import json
from typing import Union
from prettyprinter import pprint
import inspect

validate_obj = DataValidator()
SELECTED_COLUMN = ""  # global to call when access the series
ERROR_ROWS_IDXS = []  # the rows which contains error or not validate data


def clean_currency(x: str):
    """ If the value is a string, then remove currency symbol and delimiters
    otherwise, the value is numeric and can be converted
    """
    # cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        # x = str(x)
        if isinstance(x, str):
            if x.startswith("$"):
                return x.replace('$', '').replace(',', '')
        # return float(x)
        return x
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_selected_columns_as_list(member_data_file):
    """
    this function will take DataFile object, to return selected columns as list
    Args:
        member_data_file:

    Returns:
        list
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    return member_data_file.get_selected_columns_as_list


def save_data_file_rounded(file_path):
    """
    Save new data file rounded float numbers
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    data_file = Path(file_path)
    df = get_df_from_data_file(file_path)
    df_copy = df.copy()
    df_columns = df_copy.columns.tolist()
    saved_logged_msg = ''  # the info log will save, contains columns name, columns dtypes
    saved_logged_cols_base = []  # the columns with dtype log will save, contains columns name, columns dtypes
    saved_logged_cols_after = []  # the columns with converted dtype
    new_cleand_cols = []  # this list all hold all columns without any spaces or whitespaces
    # Volunteered in the past
    # cprint(df.dtypes, 'green')
    try:
        for col in df_copy.columns.tolist():

            new_cleand_cols.append(col.strip())
            saved_logged_cols_base.append(f"{col}: {df_copy[col].dtype}")
            if df_copy[col].dtype == "float64":
                # df_copy[col] = df_copy[col].round().astype('int64')
                df_copy[col] = df_copy[col].round().astype(float)
            elif df_copy[col].dtype == "object":
                df_copy[col] = df_copy[col].str.strip()
                # df_copy[col] = df_copy[col].apply(clean_currency)
            if df_copy[col].dtype == "bool":
                df_copy[col] = df_copy[col].astype(str)
            saved_logged_cols_after.append(f"{col}: {df_copy[col].dtype}")

        # the messages will save the logs of data file columns
        msg_str_before = '\n'.join(saved_logged_cols_base)
        msg_str_after = '\n'.join(saved_logged_cols_after)
        saved_logged_msg = "\nMain Column with Data type: \n[\n {} \n]\n Converted Columns data type: \n[\n {} \n]\n".format(
            msg_str_before, msg_str_after)
        log_info(saved_logged_msg)
        delete_data_file(file_path)
        if (data_file.suffix == ".xlsx") or (data_file.suffix == ".xls"):
            df_copy.to_excel(data_file.as_posix(), header=new_cleand_cols, index=False)
        elif data_file.suffix == ".csv":
            df_copy.to_csv(data_file.as_posix(), header=new_cleand_cols, index=False, sep=',')

        cprint("save done", 'green')
        cprint(data_file.as_posix(), 'yellow', 'on_grey')
    except Exception as ex:
        delete_data_file(file_path)
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def download_data_file_converter(member_data_file):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        selected_columns = member_data_file.get_selected_columns_as_list
        data_file_path = Path(member_data_file.data_file_path)
        df = get_df_from_data_file(data_file_path)
        if data_file_path.suffix == ".xlsx":

            df.to_excel(data_file_path.as_posix(), header=True, index=False, columns=selected_columns)
        elif data_file_path.suffix == ".csv":
            df.to_csv(data_file_path.as_posix(), header=True, index=False, columns=selected_columns)
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def extract_all_columns_with_dtypes(file_name):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        all_columns = {}  # hold all columns in the file

        df = get_df_from_data_file(file_name)
        # iterating the columns
        for col in df.columns:
            # print(col)
            # print(type(df.dtypes[col]))
            all_columns[col] = str(df.dtypes[col])

        # all_columns = sorted(all_columns)
        # print(all_columns)
        return all_columns

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def extract_all_column_names(file_name):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        all_columns = []  # hold all columns in the file

        df = get_df_from_data_file(file_name)
        full_file_path = Path(file_name)

        # iterating the columns
        for col in df.columns:
            # print(col)
            # print(type(df.dtypes[col]))
            all_columns.append(col)
        # all_columns = df.columns

        # all_columns = sorted(all_columns)
        # print(all_columns)
        return all_columns
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_row_count(file_path):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        full_file_path = Path(file_path)
        row_counts = None
        df = get_df_from_data_file(file_path)
        # cprint(df.dtypes, 'blue', attrs=['bold'])
        # cprint(df, 'magenta')
        row_counts = df.shape[0]
        return row_counts
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_rows_data_by_columns(file_path, columns, records_count, columns_with_types, all_original_columns):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        all_rows = []
        file_obj = Path(file_path)
        # check if file exists
        if file_obj.exists():
            df = get_df_from_data_file(file_path)
            records_count = int(records_count)
            # cprint(f"records_count > {records_count}", 'cyan')
            previous_25_count = int(records_count - 25)
            print(previous_25_count, records_count)
            # df2 = df.loc[previous_50_count:records_count, columns]
            # print(df2)
            current_record_data = {}
            for index, row in islice(df[columns].iterrows(), previous_25_count, records_count):
                # cprint(f"index:>> {index}", 'yellow')
                # index is the index in the data frame
                # row is the series object
                idx = index
                for col in columns:
                    # print(row[col])
                    # print(idx, col)
                    tmp_cell_val = row[col]
                    current_record_data["PANDAS_ID"] = idx
                    tmp_cell_val = replace_nan_value(tmp_cell_val)
                    # tmp_cell_val = tmp_cell_val.rstrip('0').rstrip('.') if '.' in tmp_cell_val else tmp_cell_val
                    # print(columns_with_types[col], tmp_cell_val)
                    current_record_data[col] = validate_obj.detect_and_validate(tmp_cell_val,
                                                                                dtype=columns_with_types[col],
                                                                                original_dtype=all_original_columns[
                                                                                    col])
                    # print(idx, "--> ", current_record_data[col])
                all_rows.insert(0, current_record_data)
                current_record_data = {}

            cprint(len(all_rows), 'yellow')
            # pprint(all_rows[0])
            # check if the length of all_rows < 0 means no records to show
            if len(all_rows) <= 0:
                return 0
            else:
                return all_rows
        else:
            return 0, 0

    except Exception as ex:
        # cprint(str(ex), 'red')
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_rows_data_by_search_query(file_path, columns, search_query, columns_with_dtypes):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        all_rows = []
        search_query = str(search_query)
        df = get_df_from_data_file(file_path)

        current_record_data = {}
        for index, row in df.iterrows():
            # index is the index in the data frame
            # row is the series object

            for col in columns:
                # print(index, "----> ", col, "--->", row[col], end='\n')

                if row.str.contains(search_query, case=False).any() is True:
                    # print(row.str.contains(search_query, case=False).any())
                    tmp_dtype = columns_with_dtypes[col]
                    tmp_cell_val = row[col]
                    current_record_data["PANDAS_ID"] = index
                    tmp_cell_val = replace_nan_value(tmp_cell_val)
                    current_record_data[col] = validate_obj.detect_and_validate(tmp_cell_val, dtype=tmp_dtype)

            if current_record_data:  # check if the dictionary is empty or contain elements
                all_rows.insert(0, current_record_data)
            current_record_data = {}

        # print(all_rows[0])
        if len(all_rows) <= 0:
            return 0
        else:
            return all_rows
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_not_validate_rows(file_path, all_columns, column_name):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        # all_columns = sorted(all_columns)
        all_rows = []
        data_file = Path(file_path)
        df = get_df_from_data_file(file_path)

        # df.fillna(method='pad')
        current_record = []  # will be dynamic record, will indicate to current row in the loop, then set it to null
        # column_mask = (df[column_name] == "NaN")
        column_mask = df[column_name].isnull()
        # df2 = df.loc[column_mask]  # data frame of elements which null
        df2 = df.loc[column_mask, all_columns]  # data frame of elements which null
        # print(type(df2))
        # print(df2)

        current_record_data = {}
        for index, row in df2.iterrows():
            # row is the series object
            for col in all_columns:
                # print(index, "----> ", col, "--->", row[col], end='\n')
                tmp_cell_val = row[col]
                current_record_data["PANDAS_ID"] = index
                current_record_data[col] = validate_obj.detect_and_validate(replace_nan_value(tmp_cell_val))
            all_rows.insert(0, current_record_data)
            current_record_data = {}

            # breakpoint()
        # print(all_rows)
        print(len(all_rows))
        return all_rows
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_not_validate_rows2(file_path, column_name, all_columns, columns_with_dtypes, records_count=25):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        global SELECTED_COLUMN, ERROR_ROWS_IDXS
        SELECTED_COLUMN = column_name
        per_page_count = 25
        # print(SELECTED_COLUMN)
        # all_columns = sorted(all_columns)
        errors_idx_lst = []
        all_rows = []
        df = get_df_from_data_file(file_path)
        records_count = int(records_count)
        # print(records_count)

        for index, row in df.iterrows():
            # print(index, row)
            # print(row.name)
            for col in all_columns:
                if col == column_name:
                    tmp_dtype = columns_with_dtypes[col]
                    curr_row = validate_obj.detect_and_validate(row[col], dtype=tmp_dtype)
                    if curr_row['is_error'] is True:
                        errors_idx_lst.append(index)

        df_error = df.copy().reindex(errors_idx_lst)
        df_correct = df.loc[~df.index.isin(errors_idx_lst)]
        cprint(f"Valid Rows {len(df_correct)}", 'green')
        cprint(f"Not Valid Rows {len(df_error)}", "red")
        # df_error = df_error.append(df_correct, ignore_index=True)
        # df2 = pd.concat([df_error, df_correct], ignore_index=False)
        # pprint(df_correct)
        # df_error = df_error.append(df_correct)
        df_concat_errors = pd.concat([df_error, df_correct])
        cprint(f"All Rows {len(df_error)}", 'yellow')
        # print(df_error)
        current_record_data = {}
        rows_count = df.shape[0]
        x_total = int(int(rows_count / per_page_count) * per_page_count)
        cprint(x_total, 'blue')
        # rows_list = (x for x in range(0, rows_count))
        rows_array = np.arange(0, rows_count)
        rows_array2 = ""
        # rows_array = np.delete(rows_array, 5)
        # cprint(len(rows_array), "green")
        # pprint(df_error.tail())
        previous_50_count = records_count - per_page_count
        print(previous_50_count, records_count)
        for index, row in islice(df_error.iterrows(), previous_50_count, records_count):
            # for index, row in results.iterrows():
            # row is the series object
            for col in all_columns:
                # print(index, "----> ", col, "--->", row[col], end='\n')
                tmp_dtype = columns_with_dtypes[col]
                tmp_cell_val = row[col]
                tmp_cell_val = replace_nan_value(tmp_cell_val)
                current_record_data["PANDAS_ID"] = index
                current_record_data[col] = validate_obj.detect_and_validate(tmp_cell_val, dtype=tmp_dtype)
            # all_rows.insert(0, current_record_data)
            all_rows.append(current_record_data)
            current_record_data = {}
        tmm = df_correct.index.tolist()
        valide_df = df.loc[tmm, all_columns]
        all_rows2 = []
        # check if it is the last page
        if x_total == records_count or x_total == 0:
            for idx, row in valide_df.iterrows():
                for col in valide_df.columns:
                    tmp_dtype = columns_with_dtypes[col]
                    tmp_cell_val = row[col]
                    tmp_cell_val = replace_nan_value(tmp_cell_val)
                    current_record_data["PANDAS_ID"] = idx
                    current_record_data[col] = validate_obj.detect_and_validate(tmp_cell_val, dtype=tmp_dtype)
                all_rows2.append(current_record_data)
                current_record_data = {}

        all_rows = all_rows + all_rows2
        all_rows.reverse()  # to reverse list make valid rows in the last
        # del results, df_copy_error_data, df_copy_correct_data, frames
        print(len(all_rows))
        # print(all_rows2[::-1])
        # pprint(all_rows2)
        if len(all_rows) <= 0:
            return 0
        else:
            if x_total <= per_page_count:
                return all_rows[::-1]
            else:
                return all_rows

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def validate_series(data_value: pd.Series):
    global ERROR_ROWS_IDXS
    # print(type(data_value), data_value)
    # print(type(data_value.name))
    if data_value.name == SELECTED_COLUMN:
        for index, row in data_value.iteritems():
            # print(type(index), type(row))
            # print(f"Index : {index}, Row : {row}")
            curr_row = validate_obj.detect_and_validate(str(row))
            if curr_row["is_error"] is True:
                ERROR_ROWS_IDXS.append(int(index))
                # print(curr_row)


def update_rows_data(file_path, data_json, column_names, columns_with_dtypes):
    # pd.describe_option("display.float_format")
    # pd.set_option("display.float_format", "{:.2f}".format)
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        data_file = Path(file_path)
        # check if file exists
        if data_file.exists():
            all_rows = []
            rows_and_values = {}
            df = get_df_from_data_file(file_path)
            for key, value in data_json.items():
                # ROW_0 [{'colName': 'Cand_Name', 'colValue': '858f'}]

                rows_and_values[key.split('_')[1]] = value

            # df2 = copy.deepcopy(df[column_names])
            # df2 = copy.deepcopy(df)
            df2 = df.copy()
            current_value = ""
            for key, value in rows_and_values.items():
                # {"0": [{"colName", "colValue"}, {"colName", "colValue"}]
                # 0 [{'colName': 'Cand_Name', 'colValue': '858fx'}]
                # print(key, value)
                for val in value:
                    # cprint(df2[val['colName']].dtype, 'yellow')
                    current_value = val['colValue']
                    if df2[val['colName']].dtype == 'int64':
                        if current_value.isdigit():
                            df2.at[int(key), val['colName']] = current_value
                        else:
                            df2[val['colName']] = df2[val['colName']].astype(str)
                            df2.at[int(key), val['colName']] = current_value
                            # df2[val['colName']] = df2[val['colName']].astype(int)
                            # df2[val['colName']] = pd.to_numeric(df2[val['colName']], errors='ignore', downcast='float')
                            # df2[val['colName']] = pd.to_numeric(df2[val['colName']])
                            # df2[val['colName']] = df2[val['colName']].astype('int64')
                    else:
                        df2.at[int(key), val['colName']] = current_value

                    # cprint(df2[val['colName']].dtype, 'blue')

            # save all changes to the file
            if data_file.suffix == ".xlsx":
                df2.to_excel(data_file.as_posix(), header=True, index=False)
            elif data_file.suffix == ".csv":
                df2.to_csv(data_file.as_posix(), header=True, index=False)
            # cprint(df2.dtypes, 'magenta')
            # return "Data saved successfully"
            return current_value, "Data saved successfully"

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def validate_data_type_in_dualbox(columns: dict, data_file_path, columns_list):
    """
        This function when the member press validate the data type in the dual
        box before click on process and navigate to the data handler page
        ["", "object", "int64", "float64", 'bool', 'datetime64', 'category', 'timedelta'];
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    result_dict = {}  # the return dict with validate values
    df = get_df_from_data_file(data_file_path)
    # print(dict(df.dtypes))

    for col_name, data_type in columns.items():
        # check what is the data type depends on that call the right method from validate obj
        if data_type == "int64":
            # tmp = df[col_name].apply(validate_obj.is_valid_number)
            # print(df[col_name][tmp])
            df[col_name].astype(str).str.isdigit()


def replace_nan_value(value):
    """
    function will return the same value from column or series of data file
    in string to avoid the error when convert string to json object in datatable js file

    Arguments:
        value {value} -- the nan value from pandas series or column

    Returns:
        value -- return the same value even if it is nan but in string
    """
    return str(value)
    # return value


def delete_data_file(path):
    """ Deletes file from filesystem. """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def reorder_columns(the_reset_of_column, is_dict=False):
    """
    this function will reorder the selected columns to make the unique column is the first one
    Args:
        the_reset_of_column:

    Returns: the_reset_of_column

    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    unique_idx = "unique identifier (id)"
    unique_col = ''

    try:
        if is_dict is False:
            for col in the_reset_of_column:
                if unique_idx in col.lower():
                    idx = the_reset_of_column.index(col)
                    unique_col = col
                    del the_reset_of_column[idx]
                    the_reset_of_column.insert(0, unique_col)

            return the_reset_of_column
        else:
            new_ordered_list = []
            for col_name, col_dtype in the_reset_of_column.items():
                if unique_idx in col_dtype:
                    new_ordered_list.insert(0, col_name)
                else:
                    new_ordered_list.append(col_name)

            return new_ordered_list

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def validate_column_date_type(columns):
    data_file = Path(file_path)
    df = None

    if data_file.exists():
        if data_file.suffix == ".xlsx":
            df = pd.read_excel(data_file.as_posix())
        elif data_file.suffix == ".csv":
            df = pd.read_csv(data_file.as_posix(), skipinitialspace=True)


def handle_uploaded_file(f, fname):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    full_path = os.path.join("media", fname)
    with open(full_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def check_int(num):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        int(num)
        return True
    except ValueError:
        return False


def delete_all_member_data_file_info(member_data_file):
    """
    this function will take DataFile object, to reset all member data file
    Args:
        member_data_file:

    Returns:
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:

        for dfile in DataHandlerSession.objects.filter(data_handler_id=member_data_file):
            delete_data_file(dfile.data_file_path)
        DataHandlerSession.objects.filter(data_handler_id=member_data_file).delete()
        # member_data_session = DataHandlerSession.objects.get(data_handler_id=member_data_file)
        # member_data_file.data_file_path = "None"
        # member_data_file.file_upload_procedure = "None"
        # member_data_file.all_records_count = 0
        # member_data_file.selected_columns = ""
        # member_data_file.selected_columns_dtypes = ""
        # member_data_file.donor_id_column = ""
        # member_data_file.is_donor_id_selected = False
        # member_data_file.unique_id_column = ""
        # member_data_file.all_columns_with_dtypes = ""
        # member_data_file.is_process_complete = False
        # member_data_file.save()
    except DataHandlerSession.DoesNotExist:
        cprint('DataHandlerSession.DoesNotExist', 'red')

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def convert_dfile_with_selected_columns(df: pd.DataFrame, selected_columns: list, file_path: Path, file_ext: str):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        parent_dir = Path() / file_path.parent
        df_selected_columns = df[selected_columns]
        if file_ext == "xlsx":
            full_file_path = Path() / f"{os.path.splitext(file_path.name)[0]}.xlsx"
            df_selected_columns.to_excel(full_file_path, header=True, index=False)
            return full_file_path
        elif file_ext == "csv":
            full_file_path = Path() / f"{os.path.splitext(file_path.name)[0]}.csv"
            df_selected_columns.to_csv(full_file_path, header=True, index=False)
            return full_file_path
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


# def get_df_from_data_file(file_path):
#     cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
#     try:
#         file_name = file_path.split('/')[-1]
#         extension = file_name.split(".")[-1]
#         cprint(file_name, 'green')
#         if extension == "csv":
#             return pd.read_csv(file_path, encoding="ISO-8859-1", skipinitialspace=True)
#         elif (extension == "xlsx") | (extension == "xls"):
#             return pd.read_excel(file_path)
#         else:
#             cprint("{} file format is not supported".format(extension), 'red', 'on_grey', attrs=['bold'])
#     except Exception as ex:
#         cprint(traceback.format_exc(), 'red')
#         log_exception(traceback.format_exc())


def get_df_from_data_file(file_path):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        data_file = Path(file_path)
        df_columns = []
        # check if the file exists
        if data_file.exists():
            # file_object = DataHandlerSession.objects.filter(data_file_path=data_file.as_posix()).first()
            # cprint(f"Helper file_object:-> {file_object}", 'magenta')
            df = None
            if (data_file.suffix == ".xlsx") or (data_file.suffix == ".xls"):
                df = pd.read_excel(data_file.as_posix())
                df_columns = df.columns.tolist()
            elif data_file.suffix == ".csv":
                df = pd.read_csv(data_file.as_posix(), sep=',', skipinitialspace=True, encoding="ISO-8859-1")
                df_columns = df.columns.tolist()

            # this for fill the empty cells with its own empty values
            float_cols = df.select_dtypes(include=['float64']).columns
            str_cols = df.select_dtypes(include=['object']).columns
            int_cols = df.select_dtypes(include=['int64']).columns
            # df.loc[:, float_cols] = df.loc[:, float_cols].fillna(0)
            # df.loc[:, int_cols] = df.loc[:, int_cols].fillna(0)
            # df.loc[:, str_cols] = df.loc[:, str_cols].fillna('NULL')
            df_clone = df.copy()

            # this loop to convert bool dtype to string
            for co in df_clone.columns.tolist():
                if df_clone[co].dtype == 'bool':
                    # cprint(df_clone[co].dtype, 'blue')
                    df_clone[co] = df_clone[co].apply(str)
                    # cprint(df_clone[co].dtype, 'green')
                elif df_clone[co].dtype == 'float64':
                    # df_clone[co] = df_clone[co].round().astype(int)
                    df_clone[co] = df_clone[co].round()

            # cprint(df_clone.dtypes, 'green')

            return df_clone

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def check_empty_df(file_path):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        df = get_df_from_data_file(file_path)
        if df.empty is True:
            return True
        return False
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def check_data_or_num(params: str):
    try:
        data_or_num = ''
        last_param = params.strip().split('/')[-1]
        if last_param == '':
            last_param = params.strip().split('/')[-2]
        if last_param.isdigit():
            data_or_num = int(last_param)
        else:
            data_or_num = 'data'
        return data_or_num
    except AttributeError:
        pass
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def remove_spaces_from_columns_names(file_path):
    """
    this function will take dataframe path and save the file without
    spaces in the columns name
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        path_obj = Path(file_path)
        df = get_df_from_data_file(file_path)
        df.columns = df.columns.str.strip()
        delete_data_file(file_path)
        if path_obj.suffix == ".xlsx":
            df.to_excel(path_obj.as_posix(), index=False)
        elif path_obj.suffix == ".csv":
            df.to_csv(path_obj.as_posix(), index=False, sep=',')
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def get_data_from_report_csv_file(history_obj: RunHistory, user: Member):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        all_donation_info = {}
        if type(history_obj).__name__ == 'RunHistory':
            history_obj = history_obj
            session_obj = history_obj.session_id
        else:
            history_obj = history_obj.first()
            session_obj = history_obj.session_id
        # check if the data file contain donation columns
        if history_obj.session_id.get_donation_columns is not None:
            all_donation_info['total_donation_columns'] = len(session_obj.get_donation_columns)
            csv_file_path = Path(history_obj.csv_report_file_path)
            if csv_file_path.exists():
                donation_cols_counts = {}
                df = pd.read_csv(csv_file_path)
                for col in session_obj.get_donation_columns:
                    # print("{:.2f}".format(3.1415926));
                    # print("{:.2f}".format(float(df[col].sum())))
                    # check if the dtype is object or startwith $, to convert the column to float
                    if df[col].dtype == 'object':
                        cprint("object section", 'green')
                        df[col] = df[col].str.replace(',', '')
                        df[col] = df[col].str.replace('$', '')
                        df[col] = df[col].apply(clean_currency).astype(float)
                    donation_cols_counts[col] = {
                        'col_name': col,
                        "total_records": df[col].count(),
                        'total_donation': "{:.2f}".format(df[col].sum()),
                        "max_value": "{:.2f}".format(df[col].max()),
                        "min_value": "{:.2f}".format(df[col].min()),
                        "mean_value": round(df[col].mean(), 2)
                    }

                all_donation_info["all_info"] = donation_cols_counts
        return all_donation_info
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def delete_unfinished_sessions(data_file_obj: DataFile):
    """
     This function will take user @data_file_obj and check uncompleted sessions and will delete them
     """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    '''
        ['id', 'data_handler_id', 'file_upload_procedure', 'data_file_path', 'base_data_file_path', 'donation_columns', 
        'current_session_name', 'run_modal_date_time', 'data_handler_session_label', 'selected_columns', 
        'selected_columns_dtypes', 'donor_id_column', 'is_donor_id_selected', 'unique_id_column', 
        'all_columns_with_dtypes', 'is_process_complete', 'all_records_count', 'upload_date', 'file_name', 
        'pdf_report_file_path', 'csv_report_file_path', 'is_validate_data', 'not_validate_columns', 
        'geo_columns', 'above_plan_limit_records', 'is_run_model']
    '''
    is_contains_unfinished_sessions = False  # if true this mean the user not complete the upload process
    data_sessions_obj = data_file_obj.data_sessions_set.all()
    for session in data_sessions_obj:
        # check if the session not complete delete the files
        if session.is_run_model is False:
            cprint("Delete unfinished sessions files...", 'yellow')
            if session.csv_report_file_path:
                delete_data_file(session.csv_report_file_path)
            if session.pdf_report_file_path:
                delete_data_file(session.pdf_report_file_path)
            if session.data_file_path:
                delete_data_file(session.data_file_path)

        history_obj = session.run_history.filter().first()
        if session.is_run_model is False:
            # check if session has a history (just in case)
            if history_obj is not None:
                delete_data_file(history_obj.pdf_report_file_path)
                delete_data_file(history_obj.csv_report_file_path)
                history_obj.delete()
            # delete_data_file(session.data_file_path)
            # delete_data_file(session.base_data_file_path)
            session.delete()
            cprint('Session Not Completed, deleting...', 'red')
            is_contains_unfinished_sessions = True
        # else:
        #     # in case session completed
        #     cprint('Session Completed!', 'green')
        #     cprint(history_obj, 'cyan')

    return is_contains_unfinished_sessions


def export_updated_data_file_csv(data_file_path: str, columns: list):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    selected_columns = columns
    new_csv_path = None
    try:
        file_path = Path() / settings.MEDIA_ROOT / "data" / f'{data_file_path}'
        response = None
        new_file_name = f"PredictME_{date.today()}.csv"
        # first check if the file is csv or xlsx file, to converted to csv file
        if file_path.suffix == ".xlsx":
            new_csv_path = file_path.parent / f"{os.path.splitext(file_path.name)[0]}.csv"
            # read_xlsx_file = pd.read_excel(file_path.as_posix())   # file with all columns
            read_xlsx_file = pd.read_excel(file_path.as_posix(), usecols=selected_columns)  # file with selected columns
            read_xlsx_file.to_csv(new_csv_path, header=True, index=False)
            # cprint('convert to csv', "yellow")
            with open(new_csv_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename=' + new_file_name
                response['File-Name'] = new_file_name

        elif file_path.suffix == ".csv":
            import random
            new_tmp_csv_path = file_path.parent / f"{random.randint(0, 100)}_{os.path.splitext(file_path.name)[0]}.xlsx"
            read_tmp_csv_file = pd.read_csv(file_path.as_posix(), usecols=selected_columns,
                                            skipinitialspace=True)  # file with selected columns
            read_tmp_csv_file.to_csv(new_tmp_csv_path, header=True, index=False)
            with open(new_tmp_csv_path.as_posix(), 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename=' + new_file_name
                response['File-Name'] = new_file_name

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())

    else:
        return response, new_file_name

    finally:
        if new_csv_path:
            new_csv_path.unlink()
            cprint("Deleting csv file...", 'red')
        elif new_tmp_csv_path:
            new_tmp_csv_path.unlink()
            cprint("Deleting Tmp csv file...", 'red')


def export_updated_data_file_xlsx(data_file_path: str, columns: list):
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    selected_columns = columns
    # download_data_file_converter(data_file)
    new_xlsx_path = None
    new_file_name = f"PredictME_{date.today()}.xlsx"
    try:
        file_path = Path() / settings.MEDIA_ROOT / "data" / f'{data_file_path}'
        response = None

        # first check if the file is csv or xlsx file, to converted to csv file
        if file_path.suffix == ".csv":
            new_xlsx_path = file_path.parent / f"{os.path.splitext(file_path.name)[0]}.xlsx"
            # read_csv_file = pd.read_csv(file_path.as_posix())  # file with all columns
            read_csv_file = pd.read_csv(file_path.as_posix(), usecols=selected_columns,
                                        skipinitialspace=True)  # file with selected columns
            # read_csv_file[selected_columns].to_excel(new_xlsx_path, header=True, index=False)  # file with selected columns
            read_csv_file.to_excel(new_xlsx_path, header=True, index=False)
            # cprint('convert to xlsx', "yellow")
            with open(new_xlsx_path, 'rb') as fh:
                response = HttpResponse(fh.read(),
                                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response['Content-Disposition'] = 'attachment; filename=' + new_file_name
                response['File-Name'] = new_file_name

        elif file_path.suffix == ".xlsx":
            import random
            new_tmp_xlsx_path = file_path.parent / f"{random.randint(0, 100)}_{os.path.splitext(file_path.name)[0]}.xlsx"
            read_tmp_xlsx_file = pd.read_excel(file_path.as_posix(),
                                               usecols=selected_columns)  # file with selected columns
            read_tmp_xlsx_file.to_excel(new_tmp_xlsx_path, header=True, index=False)
            with open(new_tmp_xlsx_path.as_posix(), 'rb') as fh:
                response = HttpResponse(fh.read(),
                                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response['Content-Disposition'] = 'attachment; filename=' + new_file_name
                response['File-Name'] = new_file_name

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())
    else:
        return response, new_file_name

    finally:
        if new_xlsx_path:
            new_xlsx_path.unlink()
            cprint("Deleting xlsx file...", 'red')
        elif new_tmp_xlsx_path:
            new_tmp_xlsx_path.unlink()
            cprint("Deleting Temp xlsx file...", 'red')


def save_donation_columns_to_json(donation_columns: str, file_name: str):
    """
    This function will save new donation columns to column_name_mapping.json file
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        file_obj = Path(file_name)
        only_file_name = file_obj.name.split(".")[0]
        data_handler_app = apps.get_app_config('data_handler')
        data_handler_path = data_handler_app.path
        json_file = Path(data_handler_path) / "PM_Model" / 'column_name_mapping.json'
        # check if json file exists
        if json_file.exists():
            with open(json_file.as_posix(), 'r+') as json_file:
                json_data = json.load(json_file)
                json_data.update({
                    only_file_name: donation_columns
                })
                json_file.seek(0)
                json.dump(json_data, json_file, indent=2)

        else:
            cprint("column_name_mapping.json file not exists", 'red')
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


def save_modal_output_to_json(file_name: str, data_to_save: dict) -> str:
    """this function will save the modal output to json file

    Args:
        file_name (str): json file path,
        data_to_save (dict) : the data will save to json file
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        data_handler_app = apps.get_app_config('data_handler')
        data_handler_path = data_handler_app.path
        modal_output_dir = Path(data_handler_path) / "PM_Model" / 'model_output_files'
        json_output_file = modal_output_dir / file_name
        json_file = open(json_output_file.as_posix(), 'w')
        json.dump(data_to_save, json_file, indent=3, sort_keys=True)
        json_file.close()

        return json_output_file.as_posix()
    except Exception as ex:
        json_output_file.unlink()
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())
        return ""


def extract_model_output_from_json(json_file_path: str) -> dict:
    """this function will return the json file content

    Args:
        json_file_path (str): json file path

    Returns:
        dict: the json file content
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    try:
        json_data = dict()
        json_file_path = Path(json_file_path)
        if json_file_path.exists():
            with open(json_file_path.as_posix(), "r") as json_file:
                json_data = json.load(json_file)

        return json_data
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())
        return json_data


def get_geo_location_data(file_path: str, geo_location_columns: list) -> dict:
    """this function will return the geo location data from data session file

    Args:
        file_path (str): data file path
        geo_location_columns (list): list of geo-location columns
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    df = None
    try:
        data_file = Path(file_path)

        # check if the file exists
        if data_file.exists():
            # check if the geo_location_columns not None
            if geo_location_columns is not None:
                if (data_file.suffix == ".xlsx") or (data_file.suffix == ".xls"):
                    df = pd.read_excel(data_file.as_posix(), usecols=geo_location_columns)
                elif data_file.suffix == ".csv":
                    df = pd.read_csv(data_file.as_posix(), sep=',', skipinitialspace=True, usecols=geo_location_columns)

                    return df.to_dict()
        else:
            # file not exists
            raise FileNotFoundError("Data file not found!")
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())
        return None
    else:
        if geo_location_columns is not None:
            return df.to_dict()
        else:
            return None


def extract_geo_location_counter(file_path: str, geo_location_columns: list) -> str:
    """this function will return how many time geo-location column repeated in model csv output file

    Args:
        file_path (str): data file path
        geo_location_columns (list): list of geo-location columns
    """
    cprint(f"### Function Name:->  {inspect.stack()[0][3]} ###", 'yellow', 'on_grey', attrs=['bold'])
    df = None
    try:
        data_file = Path(file_path)
        all_data = dict()  # this will hold the geo col as key and duplicated values as value
        predictme_col_name = 'Model Name: ensemble: Donor Predicted Classification (>= Threshold Value)'
        cprint(data_file.name, 'magenta', attrs=['bold'])
        cprint(geo_location_columns, 'magenta', attrs=['bold'])
        print('')
        # check if the geo_location_columns is not None
        if geo_location_columns is not None:
            # check if the file exists
            if data_file.exists():
                df = pd.read_csv(data_file.as_posix(), sep=',', skipinitialspace=True)
                filtered = (df[predictme_col_name] == 1)
                new_filtered_df = df.loc[filtered]
                # geo_location_columns.append(predictme_col_name)  # append the predictme column to dataframe columns
                geo_df = df.loc[filtered, geo_location_columns]

                for geo_col in geo_location_columns:
                    duplicated_values = geo_df.pivot_table(columns=[geo_col], aggfunc='size')
                    all_data[geo_col] = duplicated_values.to_dict()
                cpprint(all_data)
            else:
                # file not exists
                raise FileNotFoundError("Model output file not found!")
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())
        return None
    else:
        # for try block
        if geo_location_columns is not None:
            return all_data
        else:
            return None


def get_data_table_overview(member):
    try:
        at_or_below_plan_limit = False
        check_records_total = False  # true if the total records more than the allowed in membership
        total_cost_for_additional_rows = 0
        above_plan_limit = 0
        member = member
        records_used = 0
        records_used_and_not_run_sessions = 0  # this will be records used from data usage with sessions not finished
        # check if the usage is not None
        if member.data_usage.filter().first() is not None:
            records_used = int(member.data_usage.first().records_used)

        member_subscription_obj = member.subscription.get()
        membership_object = member_subscription_obj.membership
        data_handler_obj = member.member_data_file.get()
        data_sessions = data_handler_obj.data_sessions_set.filter()
        all_records_count = data_handler_obj.data_sessions_set.filter(is_run_model=False).values_list(
            'all_records_count', flat=True)
        # cprint(f"all records for sessions:-> {all_records_count}", 'yellow')
        all_records_count = sum(list(all_records_count))
        records_used_and_not_run_sessions = int(all_records_count + records_used)
        at_or_below_plan_limit = int(membership_object.allowed_records_count - records_used_and_not_run_sessions)

        # check if all uploaded files rows bigger or less the allowed of user membership
        if records_used_and_not_run_sessions > membership_object.allowed_records_count:
            above_plan_limit = int(records_used_and_not_run_sessions - membership_object.allowed_records_count)
            # above_plan_limit = int(above_plan_limit + all_records_count)
            total_cost_for_additional_rows = above_plan_limit * membership_object.additional_fee_per_extra_record
            check_records_total = True
        else:
            check_records_total = False

        # cprint(member_subscription_obj, 'blue')
        # cprint(membership_object, 'cyan')
        # cprint(data_handler_obj, 'green')
        # cprint(data_sessions, 'yellow')
        # cprint(all_records_count, 'magenta')
        # cprint(at_or_below_plan_limit, 'magenta')
        # cprint(total_cost_for_additional_rows, 'red')
        # cprint(at_or_below_plan_limit, 'yellow')
        # cprint(check_at_or_below_plan_limit, 'yellow')

        data = {
            "plan_name": membership_object.parent.capitalize(),
            'plan_limit': membership_object.allowed_records_count,
            # 'current_data_used': records_used,
            'current_data_used': records_used_and_not_run_sessions,
            'at_or_below_plan_limit': at_or_below_plan_limit,
            "above_plan_rows": above_plan_limit,
            "additional_fee": f"${membership_object.additional_fee_per_extra_record}",
            'total_cost_for_additional': f"${total_cost_for_additional_rows}",
            'check_records_total': check_records_total,
        }
        return data
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())
