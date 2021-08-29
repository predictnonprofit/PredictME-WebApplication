from importlib import reload
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
import time
from termcolor import cprint
import traceback
from predict_me.my_logger import log_exception
import json
from data_handler.models import (DataFile, RunHistory, DataUsage, ModelMostSimilarFile)
from datetime import datetime
import sys
import uuid
from data_handler.PM_Model.PredictME_Model import run_model
from .helpers import save_modal_output_to_json
from decimal import Decimal
from prettyprinter import pprint


class RunModelConsumer(WebsocketConsumer):

    def connect(self):
        try:
            self.user = self.scope.get("user")
            self.room_name = 'data_handler_async_room'
            self.room_group_name = 'data_handler_async_group'

            self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            self.accept()

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)

    def disconnect(self, close_code=None):
        try:
            self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            self.close()
            # self.disconnect(close_code)
            cprint("Close the connection", 'green')
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)

    def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        text_data = text_data_json.get("message")
        session_id = text_data_json.get("sessionID")
        member = self.user
        # cprint(text_data_json, 'magenta')
        try:

            if text_data == "RUN_THE_MODEL":
                member_data_file = DataFile.objects.get(member=member)
                data_session = member_data_file.data_sessions_set.filter(pk=session_id).first()
                donation_cols = data_session.donation_columns
                donation_cols_as_list = data_session.get_donation_columns
                # text_cols = data_session.text_columns
                text_cols = data_session.get_all_columns_but_donation_columns
                cprint(f"donation_cols --> {donation_cols}", 'yellow')
                cprint(f"donation_cols --> {donation_cols_as_list},  Type----> {type(donation_cols_as_list)}", 'red')
                cprint(f"text_cols --> {text_cols}", 'yellow')
                run_model_data = run_model(data_session.data_file_path, donation_cols, text_cols, self)
                if run_model_data:
                    model_output_data = run_model_data.get("OUTPUT")
                    cprint("Run model completed!", 'green')

                    # update current session data
                    data_session.pdf_report_file_path = run_model_data.get('PDF_FILE')
                    data_session.csv_report_file_path = run_model_data.get('CSV_FILE')
                    data_session.is_process_complete = True
                    data_session.is_run_model = True
                    data_session.run_modal_date_time = datetime.now()
                    data_session.save()
                    member_data_file.is_run_the_model = True
                    cprint("Save to member_data_file table", 'green', 'on_grey', attrs=['bold'])
                    member_data_file.save()

                    # save to run history
                    run_history = RunHistory()
                    run_history.member = self.user
                    run_history.session_id = data_session
                    run_history.session_name = data_session.data_handler_session_label
                    run_history.pdf_report_file_path = run_model_data.get('PDF_FILE')
                    run_history.csv_report_file_path = run_model_data.get('CSV_FILE')
                    # save the output to json file and return the json file path
                    unique_filename = str(self.user.pk) + "_" + data_session.data_handler_session_label + str(
                        uuid.uuid4()) + ".json"
                    modal_json_output_file_path = save_modal_output_to_json(unique_filename, model_output_data)
                    run_history.modal_output_json_file_path = modal_json_output_file_path
                    cprint("Save to run_history table", 'green', 'on_grey', attrs=['bold'])
                    run_history.save()

                    cprint(f"############ >> {type(model_output_data.get('donation_columns')).__name__}", 'yellow')
                    # save model similar file data to db
                    if type(model_output_data.get(
                            'donation_columns')).__name__ == 'str':  # check if the donation columns not exists
                        similar_file_obj = None
                        cprint("Donation columns not exists will save similar file!", 'blue', 'on_grey', attrs=['bold'])
                        cprint(model_output_data.get("similar_percentage"), 'magenta', attrs=['bold'])
                        # the data when create
                        created_data = {
                            'similar_file_path': model_output_data.get('similar_filename'),
                            'member': self.user,
                            'data_session': data_session,
                            'similar_percentage': Decimal(model_output_data.get("similar_percentage")),
                            'unique_features': model_output_data.get("unique_features"),
                            'feature_count': model_output_data.get("feature_count"),
                            'common_features': model_output_data.get("common_features"),
                            'categorical_data': model_output_data.get("similar_categorical_columns")

                        }

                        try:

                            similar_file_obj = ModelMostSimilarFile.objects.get(
                                similar_file_path__exact=model_output_data.get('similar_filename')
                            )
                            cprint("Will update the similar file, already exists", 'blue', 'on_grey', attrs=['bold'])
                            similar_file_obj.counter = similar_file_obj.counter + 1
                            similar_file_obj.member = self.user
                            similar_file_obj.data_session = data_session
                            similar_file_obj.similar_percentage = Decimal(model_output_data.get("similar_percentage"))
                            similar_file_obj.unique_features = model_output_data.get("unique_features")
                            similar_file_obj.feature_count = model_output_data.get("feature_count")
                            similar_file_obj.common_features = model_output_data.get("common_features")
                            similar_file_obj.categorical_data = model_output_data.get("similar_categorical_columns")
                        except ModelMostSimilarFile.DoesNotExist:
                            # in case the model not exists, create new one
                            cprint("********* Will create the similar file, not exists!", 'blue', attrs=['bold'])
                            similar_file_obj = ModelMostSimilarFile.objects.create(**created_data)
                            cprint(f"similar_file_objsimilar_file_obj ---> {similar_file_obj}", 'red', attrs=['bold'])
                        finally:
                            cprint("********** Save to model_most_similar_file table", 'green', 'on_grey',
                                   attrs=['bold'])
                            similar_file_obj.save()

                        cprint(f"$$$$$$$$$>>>> {similar_file_obj}", 'magenta', 'on_grey', attrs=['bold'])
                    else:
                        # this case when donation columns not empty
                        cprint("Donation columns exists will not save similar file!", 'blue', 'on_grey', attrs=['bold'])

                    cprint('save to db completed...', 'yellow')

                    self.send(json.dumps({"msg": "Complete Successfully!"}))
                    # self.close()
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(traceback.format_exc()), 'red')
            cprint("Call in Consumers", 'red', "on_grey", attrs=['bold'])
            member_data_file.is_run_the_model = False
            member_data_file.save()
            data_session.is_process_complete = False
            data_session.is_run_model = False
            data_session.run_modal_date_time = None
            data_session.save()
            log_exception(traceback.format_exc())
            self.close()
        else:
            # if the code run with no errors, create data usage object for the user
            records_used_list = list(
                member.member_data_file.get().data_sessions_set.filter(is_run_model=True).values_list(
                    'all_records_count', flat=True))
            obj, created = DataUsage.objects.update_or_create(
                member=self.user,
                defaults={'records_used': int(sum(records_used_list))}
            )
            self.close()
        finally:
            # reload the module to avoid any errors, when run the model
            reload(sys.modules['data_handler.PM_Model.PredictME_Model'])
            # self.close()


def send_data(obj):
    try:
        obj.send(text_data=f"member_data_file")
        time.sleep(3)
        obj.send(text_data='Now sleep after sleep 3')
        time.sleep(2)
        obj.send(text_data=f"data_session")
        time.sleep(2)
        obj.send(text_data='Request complete', close=True)
    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        cprint(str(ex), 'red')
        obj.send(text_data=str(ex))  # to display the error in the session modal
        log_exception(ex)
