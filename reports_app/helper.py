from faker import Faker
from predict_me.my_logger import log_exception
from termcolor import cprint
from membership.models import (Subscription, Membership)
from data_handler.models import (DataFile, DataHandlerSession)
from users.models import Member
from django.db.models import Q
from datetime import datetime
from django.forms.models import model_to_dict
from django.db import connection
import decimal
import json
from django.core.exceptions import ObjectDoesNotExist


def is_valid_queryparams(param):
    return param != "" and param is not None and param != 'all'

def quick_converter(obj):
    data = []
    for o in obj:
        data.append(o)

    return data

def get_info(obj):
    for op in dir(obj):
        if not op.startswith("__"):
            print(op)


# this dict will hold all terms used in the web page and what match in the DB model
DB_TERMS = {
    "gen-filter-state": 'state', 'gen-filter-users-country': 'country',
    'gen-filter-users-city': 'city', 'users-filter-sub-plan': 'sub_plan',
    'gen-filter-total-staff': 'total_staff', "gen-filter-number-volunteer": "num_of_volunteer",
    "annualRevenue": 'annual_revenue', "gen-filter-number-of-board-member": "num_of_board_members",
    "gen-filter-users-status": 'status', "gen-filter-users-org-type": "org_type",
    'gen-filter-other-org-type': 'other_org_type', 'gen-filter-start': 'start_date',
    'gen-filter-end': 'end_date'
}
USERS_STATUS = ("Active", 'Pending', 'Cancel')
SUB_PLANS = ("Starter", 'Professional', 'Expert')

DEFAULT_COLUMNS = (
    ""
)  # this will hold all default columns which will display in all reports

GENERIC_TERMS = []  # this will hold all generic filters name

ALL_MEMBERSHIP = {}  # this will hold all memberships with its own slug

all_membership_obj = Membership.objects.all()
for m in all_membership_obj:
    ALL_MEMBERSHIP[m.slug] = m.id


# this function will return filter name with lower and replaced space with underscore
def report_name(name: str):
    if type(name) is str:
        return name.lower().replace(" ", "_")
    else:
        return name


# this function will return the field name with capitalize case
def capitalize_report_name(name: str):
    return name.replace("_", " ").title()


# this function will get the percentage usage of data handler of every user
def data_handler_percent_usage(total, record_used):
    return (record_used / total) * 100


class ReportFilterGenerator:

    @staticmethod
    def get_generic_filters():
        return [
            # {"filter_name": "First Name", "report_section": "users", "input_name": report_name("First Name"),
            #  "has_options": False, "report_type": "Generic Filter"},
            # {"filter_name": "Last Name", "report_section": "users", "input_name": report_name("Last Name"),
            #  "has_options": False, "report_type": "Generic Filter"},
            # {"filter_name": "Email", "report_section": "users", "input_name": report_name("Email"),
            #  "has_options": False, "report_type": "Generic Filter"},
            {"filter_name": "User Status", "report_section": "users",
             "input_name": report_name("User Status"), "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Plan", "report_section": "users",
             "input_name": report_name("Plan"), "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Country", "report_section": "users", "input_name": report_name("Country"),
             "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "City", "report_section": "users", "input_name": report_name("City"), "has_options": True,
             "report_type": "Generic Filter"},
            {"filter_name": "Organization Type", "report_section": "users",
             "input_name": report_name("Organization Type"), "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Organization Name", "report_section": "users",
             "input_name": report_name("Organization Name"), "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Register Date", "report_section": "users", "input_name": report_name("Register Date"),
             "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Job Title", "report_section": "users", "input_name": report_name("Job Title"),
             "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Annual Revenue", "report_section": "users", "input_name": report_name("Annual Revenue"),
             "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Total Staff", "report_section": "users", "input_name": report_name("Total Staff"),
             "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Number of Volunteer", "report_section": "users",
             "input_name": report_name("Number of Volunteer"), "has_options": True, "report_type": "Generic Filter"},
            {"filter_name": "Number of Board Members", "report_section": "users",
             "input_name": report_name("Number of Board Members"), "has_options": True, "report_type": "Generic Filter"}

        ]

    @staticmethod
    def get_minimum_generic_filters(report_section_name=None):
        """
        this method will return the minimum of the generic filters to join it with specific filters section
        """
        if report_section_name is not None:
            if report_section_name == "users":
                return [
                    # {"filter_name": "First Name", "report_section": "users", "input_name": report_name("First Name"),
                    #  "has_options": False, "report_type": "Generic Filter"},
                    # {"filter_name": "Last Name", "report_section": "users", "input_name": report_name("Last Name"),
                    #  "has_options": False, "report_type": "Generic Filter"},
                    # {"filter_name": "Email", "report_section": "users", "input_name": report_name("Email"),
                    #  "has_options": False, "report_type": "Generic Filter"},
                    {"filter_name": "User Status", "report_section": "users",
                     "input_name": report_name("User Status"), "has_options": True, "report_type": "Generic Filter"},
                    {"filter_name": "Plan", "report_section": "users",
                     "input_name": report_name("Plan"), "has_options": True, "report_type": "Generic Filter"},
                ]

    @staticmethod
    def get_custom_filters(report_section_name):
        if report_section_name == "users":
            return [
                {"filter_name": "Active Users", "report_section": "users", "input_name": report_name("Active Users"),
                 "has_options": False, "report_type": "Users Filter"},
                {"filter_name": "Cancelled Users", "report_section": "users",
                 "input_name": report_name("Cancelled Users"),
                 "has_options": False, "report_type": "Users Filter"},
                {"filter_name": "Days Left", "report_section": "users", "input_name": report_name("Days Left"),
                 "has_options": False, "report_type": "Users Filter"},
            ]
        if report_section_name == "data_usage":
            return [
                {"filter_name": "Last Run", "report_section": "data_usage", "input_name": report_name("Last Run"),
                 "has_options": True, "report_type": "Data Usage Filter"},
                {"filter_name": "Usage", "report_section": "data_usage", "input_name": report_name("Usage"),
                 "has_options": True, "report_type": "Data Usage Filter"},
                {"filter_name": "Run Model", "report_section": "data_usage", "input_name": report_name("Run Model"),
                 "has_options": True, "report_type": "Data Usage Filter"},

            ]
        elif report_section_name == "revenue":
            return [
                {"filter_name": "Plan Start Date", "report_section": "revenue",
                 "input_name": report_name("Plan Start Date"),
                 "has_options": True, "report_type": "Revenue Filter"},
                {"filter_name": "Next Renewal Date", "report_section": "revenue",
                 "input_name": report_name("Next Renewal Date"),
                 "has_options": False, "report_type": "Revenue Filter"},
                {"filter_name": "Revenue Date", "report_section": "revenue", "input_name": report_name("Revenue Date"),
                 "has_options": True, "report_type": "Revenue Filter"},

            ]
        if report_section_name == "users_status":
            return [
                {"filter_name": "User Status", "report_section": "users",
                 "input_name": report_name("User Status"), "has_options": True, "report_type": "Generic Filter"},
                {"filter_name": "Register Date", "report_section": "users_status",
                 "input_name": report_name("Register Date"),
                 "has_options": True, "report_type": "Users Status"},
                {"filter_name": "Days Left", "report_section": "users_status", "input_name": report_name("Days Left"),
                 "has_options": True, "report_type": "Users Status"},
                {"filter_name": "Revenue Start Date", "report_section": "users_status",
                 "input_name": report_name("Revenue Start Date"),
                 "has_options": True, "report_type": "Users Status"},
            ]


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class ReportGenerator:
    def __init__(self, section_name, displayed_columns, filter_cookies):
        self.section_name = section_name
        if not filter_cookies:
            self.report_filters = "Empty filters!!"
        else:
            self.report_filters = filter_cookies

        if not displayed_columns:
            self.report_filters = "NO columns to display!!"
        else:
            self.displayed_columns = displayed_columns

    def __str__(self):
        return f"Reports Section: {self.section_name}, Displayed Columns: {self.displayed_columns} --> Report Filter: {self.report_filters}"

    def get_columns_data(self):
        """
            this method will return every column with its data based on the report section name
            @return {"column_name": ""}
        """
        pass

    def get_displayed_columns(self):
        """
            this method will return the displayed columns only
            @return list of columns
        """
        return self.displayed_columns

    def get_rows_file(self):
        """
            this method will return the rows of displayed columns or based on the reports filters
            @return list of dict
        """
        faker_obj = Faker()
        faker_holder = []
        for _ in range(1, 20):
            faker_holder.append({
                "id": _,
                "name": faker_obj.name(),
                "email": faker_obj.email(),
                "reg_date": faker_obj.date_this_year(),
                "status": faker_obj.word(USERS_STATUS),
                "sub_plan": faker_obj.word(SUB_PLANS),
            })
        return faker_holder

    @staticmethod
    def generate_reports(filters_array):
        print(filters_array)

    @staticmethod
    def generate_reports_table_header(filters_array):
        all_columns = []
        for col in filters_array:
            all_columns.append(col['filter_name'])

        return all_columns

    @staticmethod
    def generate_report(report_section_name, filter_list, report_table_header, user_id):
        # cprint(filter_list, "blue")
        # cprint(report_table_header, 'red')
        filter_keys = {}
        reports_holder = ''  # this to hold every report in single loop
        all_filters = {}
        # cprint(type(filter_list), 'yellow')
        for r_filter in filter_list:
            # print(r_filter)
            filter_keys[r_filter['filter_name']] = r_filter['filter_value']

        # cprint(report_table_header, 'red')
        # cprint(report_section_name, 'red')
        reports_holder = ReportGenerator.report_maker(report_section_name, filter_list, report_table_header)

        return reports_holder

    @staticmethod
    def report_maker(report_section_name: str, filter_list: list, report_table_header):
        report_data = {}  # this dict will hold every reports information

        filter_keys = {}
        # cprint(filter_list, 'yellow')
        for r_filter in filter_list:
            # print(r_filter)
            # cprint(report_name(r_filter['filter_name']))
            if (report_name(r_filter['filter_name']) == "register_date") or (
                    report_name(r_filter['filter_name']) == "annual_revenue"):
                filter_keys[report_name(r_filter['filter_name'])] = r_filter['filter_value']

                # cprint("_" in r_filter['filter_value'], 'red')
                # cprint(report_name(r_filter['filter_value']), 'green')
            elif report_name(r_filter['filter_name']) == "city":
                filter_keys[report_name(r_filter['filter_name'])] = r_filter['filter_value']
            else:
                if report_name(r_filter['filter_name']) == "organization_type":
                    filter_keys["org_type"] = r_filter['filter_value']
                elif report_name(r_filter['filter_name']) == "organization_name":
                    filter_keys[report_name("org_name")] = r_filter['filter_value']
                elif report_name(r_filter['filter_name']) == "user_status":
                    filter_keys[report_name("status")] = report_name(r_filter['filter_value'])
                else:
                    filter_keys[report_name(r_filter['filter_name'])] = report_name(r_filter['filter_value'])

            filter_keys["report_section_name"] = report_name(r_filter['report_section_name'])
        # cprint(filter_list, 'magenta')
        # first check the section of the report to call the convenient method for it
        if report_section_name == "users":
            report_data = ReportGenerator.get_all_user_query(filter_keys, report_table_header, 'users')
        elif report_section_name == 'data-usage':
            report_data = ReportGenerator.get_data_usage_query(filter_keys, report_table_header, 'data-usage')

        return report_data

    @staticmethod
    def get_all_user_query(filter_dict: dict, table_header: list, report_section_name: str):
        # section_name = filter_dict['report_section_name']
        filter_d = filter_dict
        if filter_d.get("report_section") is not None:
            del filter_d['report_section_name']  # this to delete the section name to get only the field with its values
        # cprint(filter_d, 'green')

        users_query = ""  # this to hold the Query
        data_usage_data = ReportGenerator.get_correct_sql_func(filter_d)

        # this if check if the any value not equal all, and it exists in the keys dictionary

        # this try to handle if the subscription not exists for members who have not subscription
        # cprint(data_usage_data, 'magenta')
        # if len(users_reports) > 0:
        return {"data": data_usage_data, "table_header": table_header, "total_results": len(data_usage_data)}
        # else:
        #     return {"data": "NO DATA TO DISPLAY FOR USERS!!", "table_header": table_header, "total_results": 0}

    @staticmethod
    def get_data_usage_query(filter_dict: dict, table_header: list, report_section_name: str):
        # section_name = filter_dict['report_section_name']
        filter_d = filter_dict
        if filter_d.get("report_section") is not None:
            del filter_d['report_section_name']  # this to delete the section name to get only the field with its values
        # cprint(filter_d, 'green')

        users_query = ""  # this to hold the Query
        users_data = ReportGenerator.get_correct_sql_func(filter_d)

        # this if check if the any value not equal all, and it exists in the keys dictionary

        # this try to handle if the subscription not exists for members who have not subscription

        # if len(users_reports) > 0:
        return {"data": users_data, "table_header": table_header, "total_results": len(users_data)}
        # else:
        #     return {"data": "NO DATA TO DISPLAY FOR USERS!!", "table_header": table_header, "total_results": 0}

    @staticmethod
    def get_correct_sql_func(filter_dict: dict):
        WHERE_OPERATOR = "AND"
        read_sql_query = ""
        cprint(filter_dict, 'green')
        columns_keys = list(filter_dict.keys())
        report_section_name = filter_dict.get("report_section_name", "users")
        # cprint(report_section_name, 'magenta')
        columns_keys.extend((
            "slug",
            "sub_range",
            "status"
        ))
        # cprint(columns_keys, 'red')
        all_rows = {}
        if len(filter_dict) > 0:
            if report_section_name == "users":
                read_sql_query = read_member_subscription_query("members", **filter_dict)
                # read_sql_query = ''
            elif report_section_name == "data_usage":
                read_sql_query = read_data_handler_query()
                # read_sql_query = 'read_data_handler_query()'

            # cprint(read_sql_query, 'blue')
            with connection.cursor() as cursor:
                cursor.execute(read_sql_query)
                # columns = [col for col in columns_keys]
                columns = [col[0] for col in cursor.description]
                # row = cursor.fetchall()
                #     for row in cursor.fetchall():
                #         row_dict = dict(zip(columns, row))
                #         # cprint(row_dict, 'red')
                #         for key, value in row_dict.items():
                #             if type(value).__name__ == 'datetime':
                #                 row_dict[key] = value.strftime("%m/%d/%Y")
                #             all_data.append(row_dict)
                # cprint(all_data[0], 'blue')
                row = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
                # cprint(row, 'green')
                cprint(len(row), 'red')
            # 'columns', 'db', 'iterator', 'model', 'model_fields', 'params', 'prefetch_related', 'query', 'raw_query', 'resolve_model_init_order', 'translations', 'using'

        # return all_rows
        # cprint(row[25], 'green')
        return row


def read_member_subscription_query(table, **kwargs):
    """ Generates SQL for a SELECT statement matching the kwargs passed. """
    sql_query = f"""
        SELECT
        member.id AS MID,
        member.first_name,
        member.last_name,
        member.full_name,
        member.email,
        member.status,
        member.date_joined,
        member.phone,
        member.street_address,
        member.state,
        member.city,
        member.country,
        member.org_name,
        member.job_title,
        member.org_website,
        member.org_type,
        member.annual_revenue,
        member.total_staff,
        member.num_of_volunteer,
        member.num_of_board_members,
        subs.id AS SUBSID,
        subs.member_id_id,
        subs.stripe_customer_id,
        subs.stripe_subscription_id,
        subs.stripe_plan_id_id,
        subs.subscription_status,
        subs.subscription_period_start,
        subs.subscription_period_end,
        subs.card_expire,
        subs.sub_range,
        subs.stripe_card_id,
        membership.id AS MEMBERSHIPID,
        membership.slug,
        membership.membership_type,
        membership.monthly_fee,
        membership.yearly_fee,
        membership.day_price,
        membership.stripe_plane_id,
        membership.additional_fee_per_extra_record,
        membership.allowed_records_count
    FROM
        members AS member,
        subscriptions AS subs,
        membership_membership AS membership
    GROUP BY
        member.id;
    """
    return sql_query


def read_data_handler_query():
    """
    Generate sql query for data handler and data handler sessions
    """
    sql_query = f"""
        SELECT
            data_handler.id AS DHID,
            data_handler.member_id,
            data_handler.allowed_records_count,
            data_handler.join_date,
            data_handler.has_sessions,
            data_handler.last_uploaded_session,
            data_session.id AS DSID,
            data_session.data_handler_id_id,
            data_session.file_upload_procedure,
            data_session.data_file_path,
            data_session.current_session_name,
            data_session.run_modal_date_time,
            data_session.data_handler_session_label,
            data_session.selected_columns,
            data_session.selected_columns_dtypes,
            data_session.donor_id_column,
            data_session.is_donor_id_selected,
            data_session.unique_id_column,
            data_session.all_columns_with_dtypes,
            data_session.is_process_complete,
            data_session.all_records_count,
            data_session.upload_date,
            data_session.file_name,
            member.id AS MID,
            member.first_name,
            member.last_name,
            member.email,
            member.status,
            member.date_joined,
            member.phone,
            member.street_address,
            member.state,
            member.city,
            member.country,
            member.org_name,
            member.job_title,
            member.org_website,
            member.org_type,
            member.annual_revenue,
            member.total_staff,
            member.num_of_volunteer,
            member.num_of_board_members
        FROM
            member_data_files AS data_handler,
            data_handler_sessions AS data_session,
            members AS member
        WHERE
            (data_session.data_handler_id_id = data_handler.id)
            AND (data_handler.member_id = member.id)
        GROUP BY
            member.id;
    """

    return sql_query
