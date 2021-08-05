from django.views.generic import TemplateView, View
from django.shortcuts import (reverse, redirect, render)
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
import simplejson as simple_json
from urllib.parse import quote_plus
from rest_framework import authentication
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db import connection
from faker import Faker
from prettyprinter import pprint
from termcolor import cprint
import random
import os, sys, traceback, json
from predict_me.my_logger import log_exception
from reports_app.helper import *
from users.models import Member
from django.http import JsonResponse, HttpResponse
from django.db.models import Q

USERS_STATUS = ("Active", 'Pending', 'Cancel')
SUB_PLANS = ("Starter", 'Professional', 'Expert')


def testing_reports(request):
    # fi = {'first_name': 'all', 'report_section_name': 'users', 'last_name': 'all', 'email': 'all',
    #       'status': 'active', 'plan': 'starter', 'country': 'us', 'city': 'all', 'org_type': 'Higher Education',
    #       'org_name': '', 'register_date': '08/30/2020 - 11/20/2020', 'job_title': 'all',
    #       'annual_revenue': '$50,000 - $100,000', 'total_staff': 231, 'num_of_volunteer': 2223,
    #       'num_of_board_members': 434}
    from users.models import Member
    from datetime import datetime
    from membership.models import Subscription
    # members_queryset_obj = Member.objects.defer("password").all().select_related("member_subscription")
    # members_queryset_obj = Member.objects.defer("password").all()
    # members_queryset_obj = Member.objects.defer("password").all()
    members_queryset_obj = Subscription.objects.all()
    # members_queryset_obj = Member.objects.defer("password").all().filter(member_subscription__id)
    # members_queryset_obj = Member.objects.defer("password").prefetch_related('member_subscription').all()
    # cprint(members_queryset_obj, 'red')
    cprint(members_queryset_obj.count(), 'magenta')
    for idx, me in enumerate(members_queryset_obj):
        # cprint(me, 'yellow')
        cprint(me.member_id.city, 'yellow')
        # cprint(me.stripe_plan_id.slug, 'yellow')
        # cprint(me.member_id.date_joined, 'yellow')
        # cprint(me.member_subscription.all().count(), 'white')

    status = "active"
    # country = "oman"
    # city = "Nihil"
    city = "Est"
    # plan = "professional"
    # plan = "starter"
    plan = "expert"
    start_date, end_date = "10/01/2020 - 10/30/2020".split(" - ")
    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    end_date = datetime.strptime(end_date, "%m/%d/%Y")
    org_type = "Arts and Culture"
    num_of_board_members = 559
    annual_revenue = "$50,000 - $100,000"
    job_title = "consequat"
    org_name = "April"
    num_of_volunteer = 560

    # cprint(type(all_members), "yellow")
    # get_info(members_queryset_obj)
    # cprint(is_valid_queryparams("one"), 'red')
    if is_valid_queryparams(status):
        members_queryset_obj = members_queryset_obj.filter(member_id__status=status)
    # if is_valid_queryparams(country):
    #     members_queryset_obj = members_queryset_obj.filter(member_id__country__iexact=country)
    # if is_valid_queryparams(city):
    #     members_queryset_obj = members_queryset_obj.filter(member_id___city__icontains=city)
    if is_valid_queryparams(plan):
        members_queryset_obj = members_queryset_obj.filter(stripe_plan_id__slug=plan)
    # if is_valid_queryparams(start_date) and is_valid_queryparams(end_date):
    #     members_queryset_obj = members_queryset_obj.filter(member_id__date_joined__range=(start_date, end_date))
    # if is_valid_queryparams(org_type):
    #     members_queryset_obj = members_queryset_obj.filter(member_id__org_type__iexact=org_type)
    # if is_valid_queryparams(num_of_board_members):
    #     members_queryset_obj = members_queryset_obj.filter(member_id__num_of_board_members=num_of_board_members)
    # if is_valid_queryparams(annual_revenue):
    #     members_queryset_obj = members_queryset_obj.filter(member_id__annual_revenue__iexact=annual_revenue)
    # if is_valid_queryparams(job_title):
    #     members_queryset_obj = members_queryset_obj.filter(member_id__job_title__icontains=job_title)
    # if is_valid_queryparams(org_name):
    #     members_queryset_obj = members_queryset_obj.filter(member_id__org_name__icontains=org_name)
    # if is_valid_queryparams(num_of_volunteer):
    #     members_queryset_obj = members_queryset_obj.filter(member_id__num_of_volunteer=num_of_volunteer)

    # cprint(members_queryset_obj, 'green')
    cprint(members_queryset_obj.count(), 'blue')
    cprint(members_queryset_obj.query, 'blue')

    from django.db import connection
    # cprint(connection.queries, "cyan")

    data = quick_converter(members_queryset_obj)
    # cprint(", ".join(data), 'red')
    html = " %s " % " <br /> <br />".join(str(v) for v in data)
    html += f"<br /> <br /> Rows Total: {members_queryset_obj.count()}"
    # cprint(html, 'yellow')
    # return HttpResponse(html, content_type="text/plain")
    return HttpResponse(html)
    # return JsonResponse({"data": html, "length": members_queryset_obj.count()}, status=200)


class ReportsListView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get(self, request, *args, **kwargs):
        return render(request, "reports_app/list.html")


class ReportsUsersListView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get(self, request, *args, **kwargs):
        cprint("list reports", 'yellow')
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
        generic_filters = ReportFilterGenerator.get_generic_filters()
        # custom_users_filters = ReportFilterGenerator.get_custom_filters('users')
        # generic_filters.extend(custom_users_filters)
        return render(request, "reports_app/list.html",
                      context={"dummy_data": faker_holder, 'title': "Users", "filter_columns": generic_filters})


class ReportsUserStatusListView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get(self, request, *args, **kwargs):
        cprint("list reports", 'yellow')
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
        generic_filters = ReportFilterGenerator.get_generic_filters()
        # custom_users_filters = ReportFilterGenerator.get_custom_filters('users')
        # generic_filters.extend(custom_users_filters)
        users_status_filter = ReportFilterGenerator.get_custom_filters("users_status")
        return render(request, "reports_app/list.html",
                      context={"dummy_data": faker_holder, "filter_columns": users_status_filter,
                               'title': "Users Status"})


class ReportsDataUsageView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get(self, request, *args, **kwargs):
        cprint("list reports", 'yellow')
        faker_obj = Faker()
        faker_holder = []
        for _ in range(1, 25):
            faker_holder.append({
                "id": _,
                "name": faker_obj.name(),
                "email": faker_obj.email(),
                "last_run": faker_obj.date_this_year(),
                "total_rec_used": faker_obj.random_int(0, 600),
                "sub_plan": faker_obj.word(SUB_PLANS),
                "usage": faker_obj.random_int(0, 100),
            })

        # generic_filters = ReportFilterGenerator.get_generic_filters()
        # custom_users_filters = ReportFilterGenerator.get_custom_filters('data_usage')
        # generic_filters.extend(custom_users_filters)
        data_usage_filters = ReportFilterGenerator.get_minimum_generic_filters("users")
        data_usage_filters.extend(ReportFilterGenerator.get_custom_filters("data_usage"))
        return render(request, "reports_app/list.html",
                      context={"dummy_data": faker_holder, 'title': "Data Usage", "filter_columns": data_usage_filters})


class ReportsExtraUsageView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get(self, request, *args, **kwargs):
        cprint("list reports", 'yellow')
        faker_obj = Faker()
        faker_holder = []
        tmp_item = []
        for _ in range(1, 25):
            faker_holder.append({
                "id": _,
                "name": faker_obj.name(),
                "email": faker_obj.email(),
                "last_run": faker_obj.date_this_year(),
                "total_rec_used": faker_obj.random_int(0, 600),
                "sub_plan": faker_obj.word(SUB_PLANS),
                "money": faker_obj.pyfloat(left_digits=None, right_digits=2, positive=False, min_value=10,
                                           max_value=1500),
            })

        return render(request, "reports_app/list.html", context={"dummy_data": faker_holder, 'title': 'Extra Records'})


class ReportsRevenuesView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get(self, request, *args, **kwargs):
        import random
        cities_query = Member.objects.all().values_list('city', flat=False)
        all_cities = []
        for ci in cities_query:
            all_cities.append(ci[0])
        faker_obj = Faker()
        faker_holder = []
        tmp_item = []
        for _ in range(1, 25):
            amount = faker_obj.pyfloat(left_digits=None, right_digits=2, positive=False, min_value=200,
                                       max_value=600)
            addition_records = random.choice([200, 400, 600])
            amount_addition_records = 0.5 * addition_records
            faker_holder.append({
                "id": _,
                "name": faker_obj.name(),
                "email": faker_obj.email(),
                "pay_date": faker_obj.date_this_year(),
                "sub_plan": faker_obj.word(SUB_PLANS),
                # "fee": random.choice([200, 400, 600]),
                'amount': amount,
                "addition_records": addition_records,
                "amount_addition_records": amount_addition_records,
                "total_amount": round(amount + amount_addition_records, 2)
            })

        # generic_filters = ReportFilterGenerator.get_generic_filters()
        # custom_users_filters = ReportFilterGenerator.get_custom_filters('revenue')
        # generic_filters.extend(custom_users_filters)
        revenue_filters = ReportFilterGenerator.get_custom_filters('revenue')
        return render(request, "reports_app/list.html",
                      context={"dummy_data": faker_holder, 'title': "Revenue", "filter_columns": revenue_filters,
                               "cities": all_cities})


class ProfitShareView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get(self, request, *args, **kwargs):
        faker_obj = Faker()
        faker_holder = []
        for _ in range(1, 25):
            faker_holder.append({
                "id": _,
                "name": faker_obj.name(),
                "pay_date": faker_obj.date_this_year(),
                "email": faker_obj.email(),
                "sub_plan": faker_obj.word(SUB_PLANS),
                # "fee": random.choice([200, 400, 600]),
                # 'fee': faker_obj.pyfloat(left_digits=None, right_digits=2, positive=False, min_value=10,
                #                          max_value=1500),
                "fee": faker_obj.random_int(0, 200),
                'product': faker_obj.word(("Extra Records", 'Renewal Fee')),
            })

        return render(request, "reports_app/list.html",
                      context={"dummy_data": faker_holder, 'title': 'Profit Share'})


class FetchReports(APIView):
    """
    API View to fetch required reports with its own filters and displayed columns
    and return the required data with columns

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def post(self, request, format=None):
        try:
            post_data = request.POST
            reports_section_name = request.POST.get("reports_section_name")
            all_filter_cookies = request.POST.get("all_filter_cookies")
            all_filter_cookies = json.loads(all_filter_cookies)
            displayed_columns = request.POST.get("displayed_columns")
            displayed_columns = json.loads(displayed_columns)
            cprint(reports_section_name, 'red')
            cprint(all_filter_cookies, 'yellow')
            cprint(len(all_filter_cookies), 'green')
            cprint(displayed_columns, 'blue')
            report_obj = ReportGenerator(reports_section_name, displayed_columns, all_filter_cookies)
            cprint(report_obj, 'magenta')

            return Response(
                {"table_header": report_obj.get_displayed_columns(), 'report_rows': report_obj.get_rows_file()},
                status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())


class FilterReports(APIView):
    """
    API View to fetch required reports with its own filters and displayed columns
    and return the required data with columns

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def post(self, request, format=None):
        try:
            post_data = request.POST
            # cprint(request.POST, "blue")
            filter_array = json.loads(request.POST.get("filtersArray"))
            filter_report_section = request.POST.get("reportSectionName")
            # cprint(filter_array, "yellow")
            # cprint(filter_report_section, "red")
            reports_headers = ReportGenerator.generate_reports_table_header(filter_array)
            # cprint(reports_headers, "green")
            reports = ReportGenerator.generate_report(filter_report_section, filter_array, reports_headers,
                                                      request.user.pk)
            # ReportGenerator.generate_reports(filter_array)
            # cprint(reports.keys(), 'green')
            # cprint(simple_json.dumps(reports.get("data")), 'green')
            # cprint(json.dumps(reports.get("data")), 'green')
            # cprint(type(reports.get("data")), 'cyan')
            # cprint(reports, 'blue')
            # cprint(reports_headers, 'red')
            # cprint(reports.get("data"), 'blue')
            return Response(
                {"table_header": reports_headers, "report_data": reports.get('data'),
                 "report_section_name": filter_report_section},
                status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())


class FetchReportData(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def post(self, request, *args, **kwargs):
        cities_query = Member.objects.all().values_list(request.POST.get("columnName"), flat=False)
        rows = []
        for ci in cities_query:
            rows.append(ci[0])

        return JsonResponse({"data": rows}, status=200)
