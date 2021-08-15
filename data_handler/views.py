from django.conf import settings
from django.views.generic import (TemplateView, View, DetailView)
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import (reverse_lazy, reverse)
from predict_me.helpers import is_integer_or_float
from django.db import transaction
from rest_framework.exceptions import ParseError
from rest_framework.parsers import (FileUploadParser, MultiPartParser, FormParser)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .helpers import *
import os, json, sys, traceback
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from rest_framework.permissions import IsAuthenticated
from .validators import CheckInDataError
from django.contrib.auth.decorators import login_required
from prettyprinter import pprint
from django.core.signing import Signer
from django.http import (HttpResponse, Http404, JsonResponse)
from django.utils.encoding import smart_str
import uuid
from data_handler.models import (DataFile, DataHandlerSession, RunHistory)
from django.contrib import messages
from django.core.cache import cache

DONOR_LBL = "Donation Field"
UNIQUE_ID_LBL = "Unique Identifier (ID)"


class ExportUpdatedDataFile(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            file_type = request.POST.get('file_type')
            session_id = int(request.POST.get('session_id'))
            member_data_file = DataFile.objects.get(member=request.user)
            session_obj = member_data_file.data_sessions_set.filter(pk=session_id).first()
            exported_response = None
            downloaded_file_name = None
            # check if file type
            if file_type == 'csv':
                exported_response, downloaded_file_name = export_updated_data_file_csv(session_obj.data_file_path,
                                                                                       session_obj.get_selected_columns_as_list)

            elif file_type == 'xlsx':
                exported_response, downloaded_file_name = export_updated_data_file_xlsx(session_obj.data_file_path,
                                                                                        session_obj.get_selected_columns_as_list)

            return exported_response
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')


class SessionDetailsView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        try:
            session_id = int(kwargs.get('id', None))
            member_data_file = DataFile.objects.get(member=request.user)
            member_data_session = member_data_file.data_sessions_set.filter(pk=session_id).first()

            return render(request, "data_handler/details.html", context={"session_info": member_data_session})

        except DataHandlerSession.DoesNotExist:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return redirect(reverse("data-handler-default"))


def session_details(request, id):
    # cprint(id, 'blue')
    return render(request, "data_handler/details.html")


class DataListDetailView(LoginRequiredMixin, DetailView):
    model = DataHandlerSession
    login_url = reverse_lazy('login')
    template_name = 'data_handler/list.html'


class DataListView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")

    # template_name = "data_handler/list.html"
    def get(self, request, *args, **kwargs):
        try:
            # path = save_modal_output_to_json('output_file.json', {"id": 1, "name": 'Ibrahim', 'jes': ["one", "two"]})
            # cprint(path, 'cyan')
            context = {}
            member_data_file = DataFile.objects.get(member=request.user)
            check_sessions = delete_unfinished_sessions(member_data_file)
            # show flash message in case the member has sessions not finished
            if check_sessions is True:
                context['is_deleted'] = 1
                messages.success(request, 'Deleting all sessions that not finished...', 'success')
            cprint(check_sessions, 'red')
            # member_data_session = DataHandlerSession.objects.filter(data_handler_id=member_data_file).count()
            member_data_session = member_data_file.data_sessions_set.filter()
            context['member_sessions'] = member_data_session.first()
            context['title'] = "Run "
            context['has_session'] = True
            # context['is_process_complete'] = member_data_session.first().is_process_complete
            context['is_process_complete'] = False
            return render(request, "data_handler/list.html", context=context)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())


@api_view(['POST'])
def data_handler_init(request):
    if request.method == "POST":
        picked_columns = request.POST.get("columns")
        return Response(request.POST)


class DataHandlerFileUpload(APIView):
    """
    View to upload data file for the member

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, filename, format=None):
        try:
            allowed_file_types = (
                "text/csv",
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel'
            )
            data_file = DataFile.objects.get(member=request.user)
            dfile = request.FILES['donor_file']
            # check if the file type is allowed
            if dfile.content_type in allowed_file_types:
                base_file_content = ContentFile(dfile.read())
                # this to make file name unique
                file_id = uuid.uuid4()
                new_file_name_id = f"{file_id.time_hi_version}-{dfile.name}"
                path = default_storage.save(f"data/{new_file_name_id}", base_file_content)
                # this step to save the base path with the old data type without convert the dtypes of the columns
                unique_user_data_file_ids = f"{str(data_file.id)}_{str(data_file.member.id)}"
                tmp_file = os.path.join(settings.MEDIA_ROOT, path)
                row_count = get_row_count(tmp_file)  # get total rows of the uploaded file
                allowed_records_number = int(
                    request.user.member_subscription.get().stripe_plan_id.allowed_records_count)
                saved_allowed_number = 0
                if row_count < allowed_records_number:
                    saved_allowed_number = 0
                else:
                    saved_allowed_number = int(row_count) - allowed_records_number
                # first check if the file empty or not
                if check_empty_df(tmp_file) is True:
                    resp = {"is_allowed": False, "row_count": row_count,
                            "msg": "The file is empty please re-upload correct file", "is_empty": True}
                    delete_data_file(tmp_file)
                    # delete_all_member_data_file_info(data_file)
                    return Response(resp, status=200)
                else:
                    # here the file not empty
                    save_data_file_rounded(tmp_file)
                    columns = extract_all_columns_with_dtypes(tmp_file)  # extract the columns from the uploaded file
                    params = request.POST.get('parameters')
                    session_label = request.POST.get('session-label')
                    file_name = request.POST.get('file_name')
                    data_or_num = check_data_or_num(params)
                    all_main_columns_dtypes = extract_all_columns_with_dtypes(tmp_file)
                    all_main_cols_str = ""
                    for key, value in all_main_columns_dtypes.items():
                        all_main_cols_str += f"{key}:{value}|"
                    member_data_session = DataHandlerSession.objects.create(data_handler_id=data_file,
                                                                            data_file_path=tmp_file,
                                                                            file_upload_procedure="local_file",
                                                                            all_records_count=row_count,
                                                                            data_handler_session_label=session_label,
                                                                            file_name=file_name,
                                                                            all_columns_with_dtypes=all_main_cols_str,
                                                                            above_plan_limit_records=saved_allowed_number)
                    data_file.last_uploaded_session = member_data_session.pk
                    data_file.save()
                    last_session_id = member_data_session.pk  # save last data session id
                    # check if the member has previous session before

                    # save the file path after upload it into the db

                    if row_count > data_file.allowed_records_count:
                        # return Response("Columns count bigger than the allowed")
                        resp = {"is_allowed": False, "row_count": row_count, "columns": columns,
                                'last_session_id': last_session_id}
                        return JsonResponse(data=resp, status=200)
                    else:
                        resp = {"is_allowed": True, "columns": columns, "row_count": row_count,
                                'last_session_id': last_session_id}
                        return JsonResponse(data=resp, status=200)
            else:
                # else for case the user upload not allowed file type
                cprint("Not allowed", "red")
                return Response({'is_allowed': False, "msg": "Uploaded file type not allowed!"}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())


class SaveColumnsView(APIView):
    """
    this view to save the selected columns with the data types and the unique id of the columns

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, *args, **kwargs):
        # save_point = transaction.savepoint()
        all_columns_with_dtypes = []  # save all columns with data types which will save to db
        try:
            member_data_file = DataFile.objects.get(member=request.user)
            session_id = int(request.POST.get("sessionID"))
            columns_name = request.POST.getlist(
                "columns[]")  # to save columns as text in db, [] -> this because the key send "columns[]"
            columns_name_dtypes = request.POST.get("columns_with_datatype")  # to save columns with the data types
            columns_name_dtypes_json = json.loads(columns_name_dtypes)
            params = request.POST.get('parameters')
            member_data_session = member_data_file.data_sessions_set.get(pk=session_id)
            # cprint(member_data_session, 'yellow')
            # cprint(member_data_session.donation_columns, 'red')

            if len(columns_name):
                columns_name = reorder_columns(columns_name_dtypes_json, True)
                # columns_names = "|".join(columns_name)
                # save the columns name only
                member_data_session.selected_columns = "|".join(columns_name)
                # double check if the unique id not in the columns that send from the client side
                if UNIQUE_ID_LBL.lower() not in columns_name_dtypes_json.values():
                    raise CheckInDataError("Unique ID Column not exists!!")

                # loop through columns name and the dtypes
                for col_name, col_dtype in columns_name_dtypes_json.items():
                    if col_dtype == UNIQUE_ID_LBL.lower():
                        member_data_session.unique_id_column = col_name

                    if col_dtype == DONOR_LBL.lower():
                        member_data_session.is_donor_id_selected = True

                    # save the column with data type in string
                    col_with_dtype = f"{col_name}:{col_dtype}"
                    all_columns_with_dtypes.append(col_with_dtype)
                reordered_columns = reorder_columns(all_columns_with_dtypes)
                member_data_session.selected_columns_dtypes = "|".join(reordered_columns)

                member_data_session.save()
                # transaction.savepoint_commit(save_point)
                return Response("Extracted columns done, please wait to display the data..", status=200)
            else:
                return Response("No Columns Selected", status=401)

        except Exception as ex:
            # transaction.savepoint_rollback(save_point)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # cprint(str(ex), "red")
            # print(exc_type, fname, exc_tb.tb_lineno)
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return Response(str(ex), status=401)

        finally:
            all_columns_with_dtypes = []  # to avoid any duplicate values or similar issues


class GetColumnsView(APIView):
    """
    API View to extract only columns name, to parse them to Datatable.js, then
    datatable.js request to another apiview to get the rows

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):

        try:
            member_data_file = DataFile.objects.get(member=request.user)
            params = request.POST.get('parameters')
            session_id = int(request.POST.get("session_id"))
            member_data_session = member_data_file.data_sessions_set.filter(pk=session_id).first()
            if member_data_session is not None:
                columns_list = member_data_session.get_selected_columns_with_dtypes
                # check if the member picked columns
                if len(columns_list) > 1:
                    return Response(columns_list, status=200)
                else:
                    # delete_data_file(member_data_session.data_file_path)
                    # delete_all_member_data_file_info(member_data_session)
                    return Response('No Columns', status=201)
            else:
                return Response('No Data Session for this user yet', status=201)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return Response("No Data file uploaded Yet!", status=200)


class GetAllColumnsView(APIView):
    """
    API View to extract only columns name, to parse them to Datatable.js, then
    datatable.js request to another apiview to get the rows

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        member_data_file = DataFile.objects.get(member=request.user)

        try:
            params = request.POST.get('parameters')
            session_id = int(request.POST.get("sessionID"))
            data_or_num = check_data_or_num(params)
            member_data_session = member_data_file.data_sessions_set.filter(pk=session_id).first()
            data_file_path = member_data_session.data_file_path
            # all_columns = extract_all_columns_with_dtypes(data_file_path)
            all_columns = member_data_session.get_all_data_file_columns
            selected_columns = member_data_session.get_selected_columns_with_dtypes
            unique_column = member_data_session.unique_id_column
            return Response(
                {"all_columns": all_columns, "selected_columns": selected_columns, "unique_column": unique_column},
                status=200, content_type='application/json')

        except AttributeError as aerr:
            log_exception(traceback.format_exc())
            return Response("No Data file uploaded Yet!", status=200)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())


class GetRowsView(APIView):
    """
    API View to get all rows from member data file, to Datatable.js ajax request to bring 
    the data from the member uploaded file

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):

        try:

            member_data_file = DataFile.objects.get(member=request.user)
            session_id = int(request.POST.get("session_id"))
            # cprint(f"Session id {session_id}", 'magenta')
            member_data_session = member_data_file.data_sessions_set.filter(pk=session_id).first()
            records_count = request.POST.get("recordsCount")
            cprint(f"records_count ->> {records_count}", 'cyan')
            file_path = member_data_session.data_file_path
            file_columns = member_data_session.get_selected_columns_as_list
            columns_with_dtypes = member_data_session.get_selected_columns_with_dtypes
            unique_column = member_data_session.unique_id_column
            all_original_columns = member_data_session.get_all_data_file_columns
            # check if there is no columns picked from the user, delete and re-upload the data file
            if len(file_columns) > 1:
                row_count = member_data_file.allowed_records_count
                data_file_rows = get_rows_data_by_columns(file_path, file_columns, records_count,
                                                          columns_with_dtypes,
                                                          all_original_columns)
                # cprint(data_file_rows, 'green')
                return Response({"data": data_file_rows, "total_rows": len(data_file_rows)}, status=200,
                                content_type='application/json')
                # return Response('{"data": ''}', content_type='application/json')
            else:
                delete_data_file(file_path)
                delete_all_member_data_file_info(member_data_session)
                return Response("All of the data has been delete!", status=204)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return Response("No Data to display!", status=200)


class GetRowsBySearchQueryView(APIView):
    """
    API View to get all rows from member data file, to Datatable.js ajax request to bring
    the data from the member uploaded file

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):
        try:
            # print(request.user)
            search_query = request.POST.get("searchQuery")
            session_id = int(request.POST.get('session_id'))
            member_data_file = DataFile.objects.get(member=request.user)
            member_data_session = member_data_file.data_sessions_set.filter(pk=session_id).first()
            file_path = member_data_session.data_file_path
            file_columns = member_data_session.get_selected_columns_as_list
            columns_with_dtypes = member_data_session.get_selected_columns_with_dtypes
            # check if there is no columns picked from the user, delete and reupload the data file
            if len(file_columns) > 1:
                # row_count = member_data_file.allowed_records_count
                data_file_rows = get_rows_data_by_search_query(file_path, file_columns, search_query,
                                                               columns_with_dtypes)
                # pprint(type(data_file_rows))
                return Response({"data": data_file_rows, "total_rows": data_file_rows}, status=200,
                                content_type='application/json')
            else:
                # delete_data_file(file_path)
                # delete_all_member_data_file_info(member_data_file)
                return Response("No Columns in search method", status=200)


        except AttributeError as arex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return Response("No Data file uploaded Yet!", status=200)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())


class NotValidateRowsView(APIView):
    """
    API View to get rows with not validate data, by column name
    the data from the member uploaded file

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):
        try:
            # print(request.user)
            col_name = request.POST.get("column_name")
            # print(request.POST)
            from data_handler.models import DataFile
            member_data_file = DataFile.objects.get(member=request.user)
            file_path = member_data_file.data_file_path
            file_columns = member_data_file.get_selected_columns_as_list
            # check if there is no columns picked from the user, delete and re-upload the data file
            if len(file_columns) > 1:
                row_count = member_data_file.allowed_records_count
                data_file_rows = get_not_validate_rows(file_path, file_columns, col_name)
                data_file_rows_json = json.dumps(data_file_rows)
                return Response({"data": data_file_rows, "total_rows": len(data_file_rows)}, status=200,
                                content_type='application/json')
            else:
                delete_data_file(file_path)
                delete_all_member_data_file_info(member_data_file)

        except Exception as ex:
            log_exception(ex)
            return Response("No data to display!", status=200)


class SaveNewRowsUpdateView(APIView):
    """
    API View to save all updated rows from data table form, 

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):
        try:
            from .validators import DataValidator
            validate_obj = DataValidator()
            # print(request.user)
            member_data_file = DataFile.objects.get(member=request.user)
            params = request.POST.get('parameters')
            session_id = int(request.POST.get("session_id"))

            member_data_session = DataHandlerSession.objects.filter(pk=session_id).first()
            # cprint(member_data_session, 'green')
            file_path = member_data_session.data_file_path
            columns_with_dtypes = member_data_session.get_selected_columns_with_dtypes
            updated_rows = request.POST.get("rows")

            json_data = json.loads(updated_rows)

            only_used_rows_data = {}
            for key, value in json_data.items():
                if len(value) > 0:  # check and get the updated rows only
                    only_used_rows_data[key] = value
                    for single in value:
                        tmp_dtype = columns_with_dtypes[single['colName']]
                        # print(single, tmp_dtype)
                        validate = validate_obj.detect_and_validate(single['colValue'], dtype=tmp_dtype)
                        # print(validate)

            column_names = member_data_session.get_selected_columns_as_list
            updated_data = update_rows_data(file_path, only_used_rows_data, column_names, columns_with_dtypes)
            if validate['is_error'] is False and "invalid literal for int()" not in updated_data:
                response = Response({"is_error": False, "msg": updated_data}, status=200,
                                    content_type='application/json')
            else:
                response = Response({"is_error": True, "msg": updated_data}, status=200,
                                    content_type='application/json')
            return response

        except AttributeError as arex:
            cprint(traceback.format_exc(), 'red')
            log_exception(arex)

            return Response("No Data file uploaded Yet!", status=200)
        except Exception as ex:
            log_exception(ex)
            cprint(traceback.format_exc(), 'red')
            return Response(f"{ex}", status=200)


class DeleteDataFileView(APIView):
    """
    ### Development only ###
    API View to delete the data files

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):
        try:
            member = request.user
            session_id = int(request.POST.get("session_id"))
            member_data_file = DataFile.objects.get(member=member)
            member_data_session = member_data_file.data_sessions_set.filter(pk=session_id).first()
            if member_data_session is not None:
                history_obj = member_data_session.run_history.filter()
                delete_data_file(member_data_session.data_file_path)
                # check if has history
                if history_obj is not None:
                    for history in history_obj:
                        delete_data_file(history.csv_report_file_path)
                        delete_data_file(history.pdf_report_file_path)
                        history_obj.delete()

                member_data_session.delete()

                # this only for developments, delete all data sessions and all run history #
                # member.member_history.all().delete()  # first, delete the run history rows
                # member.member_data_file.get().data_sessions_set.all()  # second, delete the data sessions
                # this only for developments, delete all data sessions and all run history #
            return Response("Session deleted successfully!", status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return Response(str(ex), status=200)


class DeleteSessionHistoryView(LoginRequiredMixin, TemplateView):
    login_url = "login"
    """
    ### Development only ###
    View to delete session with data files

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    def post(self, request, *args, **kwargs):
        try:
            is_all = False
            session_id = None
            # check if delete only one session or all sessions
            if request.POST.get("is-all") is not None:
                is_all = True
            else:
                session_id = int(request.POST.get('session_id'))

            member = request.user
            data_handler_obj = member.member_data_file.get()
            sessions_objs = data_handler_obj.data_sessions_set.all()
            history_objs = member.member_history.all()

            # check if the member want to delete all sessions and histories
            if is_all is True:
                for session in sessions_objs:
                    tmp_history_obj = session.run_history.filter().first()
                    # check if the session has history object
                    if tmp_history_obj is not None:
                        delete_data_file(tmp_history_obj.csv_report_file_path)
                        delete_data_file(tmp_history_obj.pdf_report_file_path)
                        tmp_history_obj.delete()
                    # delete session file
                    delete_data_file(session.data_file_path)
                    session.delete()
                messages.success(request, 'All Sessions Deleted Successfully!', 'success')
            else:
                session = data_handler_obj.data_sessions_set.filter(pk=session_id).first()
                session_name = session.data_handler_session_label
                history_obj = session.run_history.filter().first()
                # check if the session has history row
                if history_obj is not None:
                    delete_data_file(history_obj.csv_report_file_path)
                    delete_data_file(history_obj.pdf_report_file_path)
                    history_obj.delete()
                    session.delete()
                else:
                    # delete session data file
                    delete_data_file(session.data_file_path)
                    session.delete()
                messages.success(request, f"Session '{session_name}' has been deleted successfully!", 'success')

            return redirect("profile-overview")

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return Response(str(ex), status=200)


class ValidateColumnsView(APIView):
    """
    ### Development only ###
    API View to validate columns data type, 

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):
        try:
            member_data_file = DataFile.objects.get(member=request.user)
            member_data_session = None
            session_id = int(request.POST.get("session_id"))
            columns = request.POST.get("columns")  # as a dict
            columns_json = json.loads(columns)  # as a dict

            # cprint(columns_json, 'magenta')
            # loop and save only donation fields
            donation_fields = []   # all donation fields
            geo_location_fields = []   # all geo-location fields
            text_fields = []     # all text fields
            numeric_fields = []   # all numeric fields
            for key, value in columns_json.items():
                if "donation" in value:
                    donation_fields.append(f"'{key}'")
                if "geo-location" in value:
                    geo_location_fields.append(f"'{key}'")
                if "text" in value:
                    text_fields.append(f"'{key}'")
                if "numeric" in value:
                    numeric_fields.append(f"'{key}'")

            # convert to string and save the columns to database
            donation_fields_as_string = f"[{', '.join(donation_fields)}]"
            geo_location_fields_as_string = f"[{', '.join(geo_location_fields)}]"
            text_fields_as_string = f"[{', '.join(text_fields)}]"
            numeric_fields_as_string = f"[{', '.join(numeric_fields)}]"
            member_data_session = member_data_file.data_sessions_set.get(pk=session_id)

            # save to database
            member_data_session.donation_columns = donation_fields_as_string
            member_data_session.geo_columns = geo_location_fields_as_string
            member_data_session.text_columns = text_fields_as_string
            member_data_session.numeric_columns = numeric_fields_as_string
            member_data_session.save()
            data_file = member_data_session.data_file_path
            columns_list = member_data_session.get_selected_columns_as_list
            # save the donation columns to json file
            save_donation_columns_to_json(member_data_session.donation_columns, data_file)
            validate_columns_result = validate_data_type_in_dualbox(columns_json, data_file, columns_list)
            if len(columns_json) > 3:
                return Response({"msg": "THe message is here"}, status=200, content_type='application/json')

            else:
                return Response("Please select at least 3 columns with the data type!", status=200)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(ex)


class FetchLastPageInfoView(APIView):
    """
    ### Development only ###
    API View to fetch details about data handler table pagination last page button

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):
        try:
            pages_content_list = []
            member_data_file = DataFile.objects.get(member=request.user)
            session_id = int(request.POST.get("session_id"))
            member_data_session = member_data_file.data_sessions_set.filter(pk=session_id).first()
            session_all_records_count = int(member_data_session.all_records_count)
            pages_count = round(session_all_records_count / 25)
            cprint(f"pages_count - > {pages_count},  {type(pages_count)}", 'red')
            for pg in range(pages_count):
                tmp_pg = (session_all_records_count - (pg * 25))
                # cprint(f"pf ->> {pg}   tmp_pg ---> {tmp_pg}", 'green')
                pages_content_list.append(tmp_pg)

            cprint(f"pages_content_list -> {max(pages_content_list)}", 'blue')
            return JsonResponse(
                data={'last_page_content': int(max(pages_content_list)), "last_page_number": pages_count}, status=200)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(ex)


class NotValidateColumnsView(APIView):
    """
    ### Development only ###
    API View to save not validate columns in the db

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):
        try:
            member_data_file = DataFile.objects.get(member=request.user)
            member_data_session = None
            columns = request.POST.get("columns")  # as a string
            columns_json = json.loads(columns)  # as a dict
            # cprint(f"columns_json -> {columns_json}", 'yellow')
            session_id = int(request.POST.get("session_id"))
            # loop and save only donation fields
            donation_fields = []
            for key, value in columns_json.items():
                if "donation" in value:
                    donation_fields.append(f"'{key}'")
            donation_fields_as_string = f"[{', '.join(donation_fields)}]"
            member_data_session = member_data_file.data_sessions_set.get(pk=session_id)

            # check if there is no validate columns
            all_not_valid_cols = []
            tmp_col_string = ""
            if len(columns_json) > 0:
                # {'Home Address': {'from': 'Text', 'to': 'Numeric'}, 'City': {'from': 'Text', 'to': 'Donation'}}
                for key, value in columns_json.items():
                    tmp_col_string = f"{key}:{value}"
                    all_not_valid_cols.append(tmp_col_string)

                all_not_valid_cols = "|".join(all_not_valid_cols)
                member_data_session.is_validate_data = False
                member_data_session.not_validate_columns = all_not_valid_cols
            else:
                member_data_session.is_validate_data = True

            member_data_session.save()
            return Response({"msg": "Not validated columns saved!"}, status=200, content_type='application/json')
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return Response({"msg": "There is an error when save not valid columns!!", "error": True}, status=200,
                            content_type='application/json')


class FilterRowsView(APIView):
    """
    ### Development only ###
    API View to validate columns data type,

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, format=None):
        try:
            member = request.user
            cprint(request.POST, "blue")
            session_id = int(request.data.get("session_id"))
            member_data_file = member.member_data_file.get()
            member_data_session = member_data_file.data_sessions_set.get(pk=session_id)
            columns_with_dtypes = member_data_session.get_selected_columns_with_dtypes
            column_name = request.POST.get("column_name")
            clicked_row_count = request.POST.get("records_number")
            # clicked_row_count = 50
            all_validate_columns = get_not_validate_rows2(member_data_session.data_file_path, column_name,
                                                          member_data_session.get_selected_columns_as_list,
                                                          columns_with_dtypes, clicked_row_count)
            # return Response("Please wait while validate the date type...", status=200)
            # print(all_validate_columns[0])
            return Response({"data": all_validate_columns, "total_rows": len(all_validate_columns)}, status=200,
                            content_type='application/json')



        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return Response(str(ex), status=200)


class AcceptsDownload(APIView):
    """
        ### Development only ###
        API View to save the member accepts and download counter

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            # {'is_accept_terms': True, 'is_accept_download_template': True, 'is_download_template': False}
            download_data = json.loads(request.POST.get("accept_data"))
            from data_handler.models import MemberDownloadCounter
            member_down_counter = MemberDownloadCounter.objects.get(member=request.user)
            member_down_counter.download_counter += 1
            member_down_counter.is_download_template = download_data['is_download_template']
            member_down_counter.save()
            return Response("update done", status=200)

        except ObjectDoesNotExist as objNotex:
            log_exception(objNotex)
            # if the member not exists before
            new_rec = MemberDownloadCounter()
            new_rec.member = request.user
            new_rec.download_counter = 1
            new_rec.is_accept_terms = download_data['is_accept_terms']
            new_rec.is_accept_download_template = download_data['is_accept_download_template']
            new_rec.is_download_template = download_data['is_download_template']
            new_rec.save()
            return Response("save done", status=200)

        except Exception as ex:
            print(ex)
            log_exception(ex)
            return Response(str(ex), status=200)


class CheckMemberUpload(APIView):
    """
        ### Development only ###
        API View to Check if member upload data file or not, to set the cookie

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            member_data_file = DataFile.objects.get(member=request.user)
            params = request.POST.get('parameters')
            data_or_num = check_data_or_num(params)
            member_data_session = DataHandlerSession.objects.filter(data_handler_id=member_data_file).first()
            # cprint(request.POST, 'blue')
            return Response(member_data_session.file_upload_procedure, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(ex)


class CheckMemberProcessStatus(APIView):
    """
        ### Development only ###
        API View to Check if member complete his data handler steps, check if the member run the modal or not

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        member_data_file = DataFile.objects.get(member=request.user)
        process_status = member_data_file.is_process_complete
        choice = request.POST.get("choice", "")
        params = request.POST.get('parameters')
        data_or_num = check_data_or_num(params)
        # check if it is session number
        member_session_file = DataHandlerSession.objects.filter(data_handler_id=member_data_file).first()

        try:
            if process_status is False:
                if choice != "" or choice is not None:
                    if choice == 'Restore':
                        pass
                    elif choice == 'Fresh':
                        delete_data_file(member_data_file.data_file_path)
                        delete_all_member_data_file_info(member_data_file)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)

        # print(process_status)
        return Response(process_status, status=200)


class FetchLastSessionNameView(APIView):
    """
        API View to get the last session name of the member

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            member_data_file = DataFile.objects.get(member=request.user)
            params = request.POST.get('parameters')
            data_or_num = check_data_or_num(params)
            # check if it is session number
            member_session_file = DataHandlerSession.objects.filter(data_handler_id=member_data_file).first()
            if member_session_file is not None:
                return JsonResponse(data={"sessionName": member_session_file.current_session_name}, status=200)
            else:
                return JsonResponse(data={"sessionName": None}, status=200)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(ex)
            cprint(str(ex), 'red')


class CheckMemberRecordNumber(APIView):
    """
        API View to get the last session name of the member

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            member_data_file = DataFile.objects.get(member=request.user)
            params = request.POST.get('parameters')
            # check if it is session number
            member_session_file = DataHandlerSession.objects.filter(data_handler_id=member_data_file).first()
            if member_session_file is not None:
                return JsonResponse(data={"records": member_session_file.above_plan_limit_records,
                                          "isValidate": member_session_file.is_validate_data}, status=200)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(ex)
            cprint(str(ex), 'red')


class SetLastSessionName(APIView):
    """
        ### Development only ###
        API View to set the last session name of the member, last step

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            member_data_file = DataFile.objects.get(member=request.user)
            member_session = DataHandlerSession.objects.filter(data_handler_id=member_data_file).first()
            session_name = request.POST.get("session_name")
            member_session.current_session_name = session_name
            # member_data_file.session_date_time = parse_datetime(timezone.now())
            member_session.save()

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(ex)
            cprint(str(ex), 'red')

        # print(process_status)
        return Response(session_name, status=200)


class SetSessionLabel(APIView):
    """
        ### Development only ###
        API View to set the uploaded session label

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            from datetime import datetime
            session_id = int(request.POST.get("session_id"))
            data_handler_obj = DataFile.objects.get(member=request.user)
            session_obj = data_handler_obj.data_sessions_set.filter(pk=session_id).first()
            session_label = request.POST.get("session_label").strip()
            now = datetime.now()
            session_obj.data_handler_session_label = session_label
            session_obj.session_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            session_obj.save()
            return JsonResponse(data={"msg": 'Session label saved successfully!', 'status': True}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)


class DeleteSessionView(APIView):
    """
        ### Development only ###
        API View to set the uploaded session label

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            from datetime import datetime
            from data_handler.models import DataFile, DataHandlerSession
            member_data_file = DataFile.objects.get(member=request.user)
            session_id = request.POST.get('method')
            if session_id.isdigit():
                member_session = DataHandlerSession.objects.get(data_handler_id=member_data_file, pk=session_id)
                member_session.delete()
            elif session_id == 'all':
                member_session = DataHandlerSession.objects.filter(data_handler_id=member_data_file)
                # cprint(member_session.first().pdf_report_file_path, "green")
                # cprint(member_session.first().csv_report_file_path, "blue")
                # check if the member run the model or not, to remove the model files output
                # if member_session.first().is_process_complete:
                #     delete_data_file(member_session.first().pdf_report_file_path)
                #     delete_data_file(member_session.first().csv_report_file_path)

                for dfile in member_session:
                    delete_data_file(dfile.data_file_path)
                member_session.delete()
            return Response("Delete Session View", status=200)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)


class RenameSessionView(APIView):
    """
        ### Development only ###
        API View to rename session

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            from datetime import datetime
            from data_handler.models import DataFile, DataHandlerSession
            member_data_file = DataFile.objects.get(member=request.user)
            session_name = request.POST.get('session_name')
            params = request.POST.get('parameters')
            data_or_num = check_data_or_num(params)
            # check if it is session number
            member_session = DataHandlerSession.objects.filter(data_handler_id=member_data_file).first()
            member_session.data_handler_session_label = session_name.strip()
            member_session.save()

            return Response("Session Renamed Successfully!", status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)


class CheckValidDataView(APIView):
    """
        ### Development only ###
        API View to check if the data is valid

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            from datetime import datetime
            from data_handler.models import DataFile, DataHandlerSession
            member_data_file = DataFile.objects.get(member=request.user)
            session_name = request.POST.get('session_name')
            # cprint("CheckValidDataView", "cyan")
            # check if it is session number
            member_session = DataHandlerSession.objects.filter(data_handler_id=member_data_file).first()
            if member_session is not None:
                # cprint(member_session.is_validate_data, "cyan")
                # member_session.save()
                status = False
                if member_session.is_validate_data is True:
                    status = True
                return JsonResponse(
                    data={"msg": f"The is validate data is {member_session.is_validate_data}", "status": status},
                    status=200)
            else:
                return JsonResponse(data={"msg": "it is None!", 'status': False}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)


class FetchDataSessionInfoView(APIView):
    """
        ### Development only ###
        API View to fetch the information about the current session

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            from datetime import datetime
            from data_handler.models import DataFile, DataHandlerSession
            member_data_file = DataFile.objects.get(member=request.user)
            session_id = int(request.POST.get("session_id"))
            data = dict()
            member_session = DataHandlerSession.objects.filter(pk=session_id).first()
            if member_session is not None:
                data['is_process_complete'] = member_session.is_process_complete
                data['current_session_name'] = member_session.current_session_name
                data['is_validate_data'] = member_session.is_validate_data
                return JsonResponse(data={"data": data}, status=200)
            else:
                return JsonResponse(data={'data': None}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)


class FetchTableOverviewDataView(APIView):
    """
        ### Development only ###
        API View to fetch the information about the current session

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            at_or_below_plan_limit = False
            check_records_total = False  # true if the total records more than the allowed in membership
            total_cost_for_additional_rows = 0
            above_plan_limit = 0
            member = request.user
            records_used = 0
            records_used_and_not_run_sessions = 0  # this will be records used from data usage with sessions not finished
            # check if the usage is not None
            if member.data_usage.filter().first() is not None:
                records_used = int(member.data_usage.first().records_used)

            member_subscription_obj = member.member_subscription.get()
            membership_object = member_subscription_obj.stripe_plan_id
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
            return JsonResponse(data={'data': data, 'status': 200}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)
            return JsonResponse(data={'data': None, 'status': 202}, status=202)


class GetTablePagination(APIView):
    """
        ### Development only ###
        API View to fetch the information about the current session

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            session_id = int(request.POST.get("session_id"))
            data_handler_obj = DataFile.objects.get(member=request.user)
            session_obj = data_handler_obj.data_sessions_set.filter(pk=session_id).first()
            # cprint(session_id, 'blue')
            # cprint("pagination", 'yellow')
            per_page = 25
            total_records = int(session_obj.all_records_count)
            total_pages = round(total_records / per_page)
            data = {
                "per_page": per_page,
                "total_records": total_records,
                'total_pages': total_pages,
            }
            return JsonResponse(data={'data': data, 'status': 200}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)
            return JsonResponse(data={'data': None, 'status': 202}, status=202)


@login_required
def download_report_file(request, report_type, run_history_id=""):
    try:
        member_data_file = DataFile.objects.get(member=request.user)
        if run_history_id != 0:
            member_session = RunHistory.objects.filter(pk=int(run_history_id)).first()
        else:
            member_session = DataHandlerSession.objects.get(data_handler_id=member_data_file)

        file_path = ""
        mime_type = ''
        # if member_session.is_process_complete:

        if report_type == "pdf":
            file_path = member_session.pdf_report_file_path
            file_obj = Path(file_path)
            mime_type = 'application/pdf'
        elif report_type == 'csv':
            file_path = member_session.csv_report_file_path
            file_obj = Path(file_path)
            mime_type = "text/csv"
        # cprint(file_obj.exists(), 'red')
        # cprint(file_obj, 'yellow')
        if file_obj.exists():
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=' + smart_str(os.path.basename(file_path))
                # response['X-Sendfile'] = smart_str(file_path)
                # cprint(dir(response), 'blue')
                # cprint(response.items(), 'blue')
                return response

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        cprint(str(ex), 'red')
        log_exception(ex)


class IsAllowedToRunModel(APIView):
    """
        ### Development only ###
        API View to fetch the information about the current session

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            from predictme_context_processors.context_processors import check_member_if_allowed_to_run_pm_model
            is_allowed = check_member_if_allowed_to_run_pm_model(request)
            # cprint(f"is_allowed:-> {is_allowed}", 'yellow')
            return JsonResponse(data={"is_allowed": is_allowed}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)


class CheckIfSessionDataTypeValid(APIView):
    """
        ### Development only ###
        API View to fetch the information about the current session

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            member = request.user
            if request.data.get("sessionID") is not None:
                session_id = int(request.data.get("sessionID"))
                member_data_file = member.member_data_file.get()
                member_data_session = member_data_file.data_sessions_set.get(pk=session_id)
                return JsonResponse(data={"is_validate_data": member_data_session.is_validate_data,
                                          "not_validate_columns": member_data_session.not_validate_columns}, status=200)
            else:
                return JsonResponse(data={"msg": "No Session is here!!"}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())


class FetchDashboardSessionData(APIView):
    """
        ### Development only ###
        API View to fetch the train and test of session

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            data = dict()
            train_test_data = dict()
            important_features_data = dict()
            geo_location_data = dict()
            history_id = int(request.data.get('historyID'))
            key_name = request.data.get('keyName')
            run_history_obj = RunHistory.objects.filter(pk=history_id).first()
            json_file_path = run_history_obj.modal_output_json_file_path
            file_obj = Path(json_file_path)
            # open the json data file
            with open(file_obj.as_posix(), 'r') as json_file:
                data = json.load(json_file)
                pprint(data)
            # check what is the key name to fetch
            if key_name == 'training_testing':
                cprint(f"training_testing request", 'cyan', attrs=['bold'])
                train_test_data['training'] = is_integer_or_float(data.get("training"))
                train_test_data['testing'] = is_integer_or_float(data.get("testing"))
                train_test_data['donation_columns'] = data.get("donation_columns")
                pprint(train_test_data)
                return JsonResponse(data={"data": train_test_data}, status=200)

            elif key_name == 'important_features':
                cprint(f"important_features request", 'magenta', attrs=['bold'])
                important_features_data['labels'] = data.get('feature_importance_labels')
                important_features_data['values'] = data.get('feature_importance_values')
                important_features_data['donation_columns'] = data.get("donation_columns")
                pprint(important_features_data)
                return JsonResponse(data={"data": important_features_data}, status=200)

            elif key_name == 'geo_location_fields':
                cprint(f"geo_location_fields request", 'green', attrs=['bold'])
                data_file = run_history_obj.session_id.data_file_path
                geo_location_fields = run_history_obj.session_id.get_geo_columns
                geo_location_data = get_geo_location_data(data_file, geo_location_fields)
                # cprint(geo_location_data, 'yellow')
                csv_file_path = run_history_obj.csv_report_file_path
                geo_data = extract_geo_location_counter(csv_file_path, geo_location_fields)
                # cpprint(geo_data)
                return JsonResponse(data={"data": {'geo_location_data': geo_location_data}}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
