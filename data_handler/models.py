from django.db import models
from django.contrib.auth import get_user_model
import pandas as pd
import json
import traceback
from termcolor import cprint
from predict_me.my_logger import log_exception
from users.models import Member
from django.utils import timezone

UPLOAD_PROCEDURES = (
    ("local_file", "Local File"),
    ("google_plus", "Google Plus",),
    ("one_drive", "One Drive"),
    ("dropbox", "Dropbox"),
    ("none", "None")
)

DATA_HANDLER_SESSION_NAMES = (
    ("upload", "Upload"),
    ("pick_columns", "Pick Columns"),
    ("data_process", "Data Processing"),
    ("run_modal", "Run Predictive Modal")
)


class DataFile(models.Model):
    member = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True,
                               related_name='member_data_file')
    allowed_records_count = models.IntegerField(null=True, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    has_sessions = models.BooleanField(default=False)
    last_uploaded_session = models.IntegerField(null=True, blank=True)
    is_run_the_model = models.BooleanField(null=True, blank=True, default=False)

    class Meta:
        db_table = 'member_data_files'

    def __str__(self):
        return f"Data file object for {self.member}, Allowed Records count {self.allowed_records_count}"

    @property
    def get_fields_as_list(self):
        fields = self._meta.fields
        fields_list = []
        for fid in fields:
            fields_list.append(fid.name)
        return fields_list


class DataHandlerSession(models.Model):
    data_handler_id = models.ForeignKey(to=DataFile, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='data_sessions_set')
    file_upload_procedure = models.CharField(max_length=20, null=True, blank=True, choices=UPLOAD_PROCEDURES)
    data_file_path = models.CharField(max_length=255, blank=True, null=True)
    donation_columns = models.CharField(max_length=255, blank=True, null=True)
    current_session_name = models.CharField(max_length=70, null=True, blank=True, choices=DATA_HANDLER_SESSION_NAMES)
    data_handler_session_label = models.CharField(max_length=70, null=True, blank=True,
                                                  default="Default Name For this session")
    selected_columns = models.TextField(null=True, blank=True)
    selected_columns_dtypes = models.TextField(null=True, blank=True)
    donor_id_column = models.CharField(max_length=150, null=False, blank=True)
    is_donor_id_selected = models.BooleanField(null=True, blank=True, default=False)
    unique_id_column = models.CharField(max_length=200, null=True, blank=True)
    all_columns_with_dtypes = models.TextField(null=True, blank=True)
    is_process_complete = models.BooleanField(null=True, blank=True, default=False)
    all_records_count = models.BigIntegerField(null=True, blank=True, default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=50, blank=True, null=True)
    pdf_report_file_path = models.CharField(max_length=255, blank=True, null=True)
    csv_report_file_path = models.CharField(max_length=255, blank=True, null=True)
    is_validate_data = models.BooleanField(null=True, blank=True)
    not_validate_columns = models.CharField(null=True, blank=True, max_length=255)
    geo_columns = models.CharField(null=True, blank=True, max_length=255)
    text_columns = models.CharField(null=True, blank=True, max_length=255)
    numeric_columns = models.CharField(null=True, blank=True, max_length=255)
    above_plan_limit_records = models.IntegerField(null=True, blank=True)
    is_run_model = models.BooleanField(null=True, blank=True, default=False)
    run_modal_date_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'data_handler_sessions'

    def __str__(self):
        return f"DataSession Object Labeled --> {self.data_handler_session_label}"

    @property
    def get_all_columns_but_donation_columns(self):
        all_cols = []  # will hold all columns
        all_cols_str = ""
        numeric_columns = self.get_numeric_columns
        text_columns = self.get_text_columns
        geo_columns = self.get_geo_columns
        if numeric_columns:
            all_cols = text_columns + numeric_columns
        else:
            all_cols = text_columns
        for col in all_cols:
            all_cols_str += f"'{col}', "
        all_cols_str = all_cols_str.rstrip(', ')  # remove the comma from last item
        all_cols_str = "[" + all_cols_str + "]"
        return all_cols_str

    @property
    def get_donation_columns(self):
        if self.donation_columns == "[]":
            return None
        else:
            cols = self.donation_columns.replace("[", "").replace("]", "").replace("'", "").split(", ")
            return cols

    @property
    def get_text_columns(self):
        if self.text_columns == "[]":
            return None
        else:
            cols = self.text_columns.replace("[", "").replace("]", "").replace("'", "").split(", ")
            return cols

    @property
    def get_geo_columns(self):
        if self.geo_columns == "[]":
            return None
        else:
            cols = self.geo_columns.replace("[", "").replace("]", "").replace("'", "").split(", ")
            return cols

    @property
    def get_numeric_columns(self):
        if self.numeric_columns == "[]":
            return None
        else:
            cols = self.numeric_columns.replace("[", "").replace("]", "").replace("'", "").split(", ")
            return cols

    @property
    def get_fields_as_list(self):
        fields = self._meta.fields
        fields_list = []
        for fid in fields:
            fields_list.append(fid.name)
        return fields_list

    @property
    def get_selected_columns_as_list(self):
        # return self.selected_columns.split("|")
        # return sorted(self.selected_columns.split("|"))
        try:
            return self.selected_columns.split("|")
        except AttributeError as aex:
            pass
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())

    @property
    def get_selected_columns_with_dtypes(self):
        columns_with_dtypes = {}

        try:
            if self.selected_columns_dtypes is not None:
                all_text = self.selected_columns_dtypes.split("|")
                for txt in all_text:
                    col_name, col_dtype = txt.split(":")
                    columns_with_dtypes[col_name] = col_dtype

        except ValueError:
            pass
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return columns_with_dtypes

    @property
    def get_all_columns_with_dtypes(self):
        columns_with_dtypes = {}

        try:
            all_cols = self.selected_columns_dtypes.split("|")
            for col in all_cols:
                col_name, col_dtype = col.split(":")
                columns_with_dtypes[col_name] = col_dtype

        except ValueError:
            pass
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return columns_with_dtypes

    @property
    def get_selected_columns_casting(self):
        columns_casting_dtypes = {}
        try:
            all_cols = self.selected_columns_dtypes.split("|")

            for col in all_cols:
                col_name, col_dtype = col.split(":")
                col_name = col_name.strip()
                # check what the kind of selected column, to place the convenient data type for casting
                if col_dtype.startswith('numeric') or col_dtype.startswith('donation'):
                    # columns_casting_dtypes[col_name] = lambda x: round(int(x)) if isinstance(x, int) else str(x) or round(int(x)) if isinstance(x, float) else str(x)
                    columns_casting_dtypes[col_name] = pd.to_numeric()
                elif col_dtype.startswith('text'):
                    columns_casting_dtypes[col_name] = str

        except ValueError:
            pass
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return columns_casting_dtypes

    @property
    def get_all_data_file_columns(self):
        cols_all_dtype = {}
        try:
            all_cols_str = self.all_columns_with_dtypes.split("|")
            for col in all_cols_str:
                if col != "":
                    col_nm, col_tp = col.split(":")
                    cols_all_dtype[col_nm] = col_tp

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
        finally:
            return cols_all_dtype


class MemberDownloadCounter(models.Model):
    member = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True,
                               related_name='download_counter')
    is_accept_terms = models.BooleanField(null=True, blank=True, default=False)
    is_accept_download_template = models.BooleanField(null=True, blank=True,
                                                      default=False)  # this when the member check he download
    is_download_template = models.BooleanField(null=True, blank=True,
                                               default=False)  # this if the member download the template or not
    download_counter = models.IntegerField(null=True, blank=True, default=0)
    date_inserted = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        db_table = 'members_download_counter'


class RunHistory(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(to=Member, on_delete=models.DO_NOTHING, null=True, blank=True,
                               related_name='member_history')
    session_id = models.ForeignKey(to=DataHandlerSession, on_delete=models.DO_NOTHING, null=True, blank=True,
                                   related_name="run_history")
    session_name = models.CharField(null=True, blank=True, max_length=100)
    run_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    pdf_report_file_path = models.CharField(max_length=200, null=True, blank=True)
    csv_report_file_path = models.CharField(max_length=200, null=True, blank=True)
    modal_output_json_file_path = models.CharField(null=True, blank=True, max_length=250)

    class Meta:
        db_table = "run_history"

    def __str__(self):
        return f"RunHistory Object for {self.member}"

    @property
    def get_session_name(self):
        return self.session_name


class DataUsage(models.Model):
    member = models.ForeignKey(to=Member, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='data_usage')
    records_used = models.BigIntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'data_usage'

    def __str__(self):
        return f"Data Usage for {self.member}"


class ModelMostSimilarFile(models.Model):
    member = models.ForeignKey(to=Member, on_delete=models.DO_NOTHING, null=True, blank=True,
                               related_name='member_model_similar_files')
    data_session = models.ForeignKey(to=DataHandlerSession, on_delete=models.DO_NOTHING, null=True, blank=True,
                                     related_name='data_session_model_similar_files')
    similar_file_path = models.CharField(max_length=255, unique=True, null=False, blank=False)
    similar_percentage = models.DecimalField(max_digits=10, decimal_places=7)
    unique_features = models.PositiveBigIntegerField(default=0)
    feature_count = models.PositiveBigIntegerField(default=0)
    common_features = models.PositiveBigIntegerField(default=0)
    categorical_data = models.CharField(max_length=255, default="[]")
    counter = models.PositiveBigIntegerField(default=1, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'model_most_similar_file'
