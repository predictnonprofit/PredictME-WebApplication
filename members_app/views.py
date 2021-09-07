from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.models import Member
from django.shortcuts import render, redirect, reverse
from data_handler.helpers import extract_model_output_from_json
from pathlib import Path
from termcolor import cprint
import os
import pandas as pd
from django.conf import settings
from datetime import date
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
import traceback
from predict_me.my_logger import (log_info, log_exception)
from django.contrib import messages
import pytz
from datetime import datetime
from .helper import calculate_records_left_percentage
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.http import JsonResponse
from data_handler.helpers import get_data_from_report_csv_file
from predict_me.constants.countries import (ALL_COUNTRIES, ALL_STATS)
from django.contrib.auth.hashers import (check_password, make_password)
import re
import stripe
from django.conf import settings
from membership.models import Membership
from django.db.models import Q
from predict_me.helpers import check_internet_access
from data_handler.models import (DataFile, RunHistory, DataHandlerSession)
from membership.models import Subscription
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

ANNUAL_REVENUE = (
    '$5,000 - $50,000', '$50,000 - $100,000',
    '$100,000 - $250,000', '$250,000 - $500,000',
    '$500,000 - $1 million', '$1 million - $5 million',
    '$5 million - $10 million', '$10 million or more'
)

ORGANIZATION_TYPES = sorted(
    (
        'Higher Education', 'Other Education', 'Health related',
        'Hospitals and Primary Care', 'Human and Social Services',
        'Environment', 'Animal', 'International', 'Religion related',
        'Other'
    )
)


@login_required
def download_instructions_template(request):
    file_path = os.path.join(settings.MEDIA_ROOT, "files", 'Donor File Template.xlsx')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response


@login_required
def download_dashboard_pdf(request):
    try:
        from django.core.files.storage import FileSystemStorage
        request.build_absolute_uri('/')
        html_string = render_to_string('members_app/profile/dashboard.html')

        html = HTML(string=html_string)
        html.write_pdf(target='/tmp/dashboard.pdf');

        fs = FileSystemStorage('/tmp')
        with fs.open('dashboard.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="dashboard.pdf"'
            return response

    except Exception as ex:
        cprint(traceback.format_exc(), 'red')
        log_exception(traceback.format_exc())


class ProfileOverview(LoginRequiredMixin, TemplateView):
    """
    this view for profile of the member
    """
    login_url = "login"
    template_name = 'members_app/profile/overview.html'

    def get_context_data(self, **kwargs):
        try:
            member = self.request.user
            context = {}
            member = Member.objects.get(email=member.email)
            # se = DataHandlerSession.objects.get(pk=1056)
            # cprint(type(se.get_all_columns_but_donation_columns), 'yellow', attrs=['bold'])
            # cprint(se.get_all_columns_but_donation_columns, 'green', attrs=['bold'])
            current_data_use = 0
            total_data_predicted = 0
            records_used_list = list(
                member.member_data_file.get().data_sessions_set.filter(is_run_model=True).values_list(
                    'all_records_count', flat=True))
            total_data_predicted = int(sum(records_used_list))
            subscription_obj = member.member_subscription.get()
            member_data_file = DataFile.objects.get(member=member)
            member_data_session = member_data_file.data_sessions_set.all()
            data_usage_obj = member.data_usage.filter().first()
            today = datetime.now(tz=pytz.UTC)
            context['member'] = member
            context['sub_obj'] = subscription_obj
            context['run_model_times'] = member.member_history.all().count()

            # cprint(subscription_obj.subscription_period_end, 'cyan')
            # check if the subscription end date is not none
            if subscription_obj.subscription_period_end is not None:
                between = subscription_obj.subscription_period_end - today  # this to get how many days left to end of subscription
            else:
                between = 0

            # check if the data_usage_obj is not None
            if data_usage_obj is not None:
                current_data_use = data_usage_obj.records_used

            if member_data_file.data_sessions_set.count() > 0:
                context['has_session'] = True
                context['is_process_complete'] = member_data_session.first().is_process_complete
                context['data_session'] = member_data_session.first()
                context['days_left'] = between.days,
                context['current_data_use'] = current_data_use
            else:
                context['has_session'] = False
                context['is_process_complete'] = False
                context['data_session'] = None
                context['days_left'] = between
                context['current_data_use'] = 0

            context['title'] = "Profile Overview"
            context['total_data_predicted'] = total_data_predicted

            return context
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())

    # def get(self, request, *args, **kwargs):

    #
    # def post(self, request):
    #     try:
    #         if request.is_ajax():
    #             cprint(f"request.is_ajax() request.is_ajax()", 'green', 'on_grey')
    #             member = Member.objects.get(email=request.user.email)
    #             member_data_file = DataFile.objects.get(member=member)
    #             member_data_session = member_data_file.data_sessions_set.all()
    #             # check if there is session to return the correct value to display on the dashboard
    #             if member_data_session.count() > 0:
    #                 records_left = calculate_records_left_percentage(member_data_file, member_data_session.first())
    #                 return JsonResponse(data={"value": int(records_left)}, status=200)
    #             else:
    #                 return JsonResponse(data={"value": int(0)}, status=200)
    #
    #     except Exception as ex:
    #         cprint(traceback.format_exc(), 'red')
    #         log_exception(traceback.format_exc())


class RunHistoryView(LoginRequiredMixin, ListView):
    login_url = "login"
    model = RunHistory
    template_name = 'members_app/profile/run_history.html'

    def get_queryset(self):
        member = self.request.user
        queryset = RunHistory.objects.filter(member=member).order_by('-run_date')
        return queryset


class UserSessionDetailsView(LoginRequiredMixin, DetailView):
    login_url = "login"
    template_name = "members_app/profile/dashboard.html"
    model = RunHistory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extracted_data"] = dict()
        data_session_obj = context['object'].session_id
        context['title'] = data_session_obj.data_handler_session_label
        history_obj = context['object']
        model_output_data = extract_model_output_from_json(history_obj.modal_output_json_file_path)
        member_obj = history_obj.member
        context['model_output_data'] = model_output_data
        context['donation_info'] = get_data_from_report_csv_file(history_obj, member_obj)
        return context


class ActivityDashboard(LoginRequiredMixin, TemplateView):
    login_url = "login"

    def get(self, request):
        try:
            context = dict()
            context['title'] = "Account Activity"
            return render(request, "members_app/profile/account_activity.html", context=context)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')


class MemberInboxView(LoginRequiredMixin, TemplateView):
    login_url = "login"

    def get(self, request):
        try:
            context = dict()
            context['title'] = "Inbox"
            return render(request, "members_app/inbox/inbox.html", context=context)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')


class AccountSettingsDashboard(LoginRequiredMixin, TemplateView):
    login_url = "login"

    def get(self, request):
        try:
            context = dict()
            stripe_card_obj = stripe_customer = None
            member = Member.objects.get(email=request.user.email)
            all_countries = ALL_COUNTRIES
            member_subscription = member.member_subscription.get()
            check_connection = check_internet_access()
            # check internet connection
            if check_connection is True:
                try:
                    stripe_card_obj = stripe.Customer.retrieve_source(
                        member_subscription.stripe_customer_id,
                        member_subscription.stripe_card_id,
                    )
                    context['last4'] = stripe_card_obj['last4']
                    context['has_connection'] = True

                except stripe.error.InvalidRequestError:
                    context['last4'] = 'Error when get the last 4 digits!'
                    cprint(traceback.format_exc(), 'red')
                    log_exception(traceback.format_exc())

                stripe_customer = stripe.Customer.retrieve(member_subscription.stripe_customer_id)  # enable this
                context['stripe_name'] = stripe_customer['name']  # enable this
            else:
                # if there is no internet connection
                context['stripe_name'] = context['last4'] = context['has_connection'] = None
                messages.warning(request, 'You do not have internet connection!', 'warning')

            context['member'] = member
            context['annual_revenue'] = ANNUAL_REVENUE
            context['org_types'] = ORGANIZATION_TYPES
            context['title'] = "Account Settings"
            context['all_countries'] = all_countries
            context['all_stats'] = ALL_STATS

            return render(request, "members_app/profile/account_settings.html", context=context)
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')

    def post(self, request, *args, **kwargs):
        try:
            context = dict()
            member = Member.objects.get(email=request.user.email)
            title = "Account Settings"
            # cprint(request.POST.get("form-name"), 'blue')
            # cprint(request.POST, 'blue')
            # ict_keys(['csrfmiddlewaretoken', 'form-name', 'first-name', 'last-name', 'country', 'state', 'email',
            # 'phone', 'org_name', 'org_website', 'org_type', 'annualRevenue', 'job_title', 'total_staff',
            # 'num_of_volunteer', 'num_of_board_members'])

            # check if the form submit name
            if request.POST.get("form-name") == 'contact-org-form':
                member.first_name = request.POST.get("first-name").strip()
                member.last_name = request.POST.get("last-name").strip()
                member.full_name = f'{request.POST.get("first-name").strip()} {request.POST.get("last-name").strip()}'
                member.email = request.POST.get("email").strip()
                member.phone = request.POST.get("phone").strip()
                member.country = request.POST.get("country").strip()
                if request.POST.get('state') is not None:
                    member.state = request.POST.get("state").strip()
                else:
                    member.state = ''
                member.street_address = request.POST.get("street_address").strip()
                member.zip_code = request.POST.get("zip_code").strip()
                member.org_name = request.POST.get("org_name").strip()
                member.org_website = request.POST.get("org_website").strip()

                if request.POST.get("org_type") == 'Other':
                    member.org_type = 'Other'
                    member.other_org_type = request.POST.get("other_org_type")
                else:
                    member.org_type = request.POST.get("org_type").strip()
                    member.other_org_type = ''

                member.annualRevenue = request.POST.get("annualRevenue").strip()
                member.job_title = request.POST.get("job_title").strip()
                member.total_staff = request.POST.get("total_staff").strip()
                member.num_of_volunteer = request.POST.get("num_of_volunteer").strip()
                member.num_of_board_members = request.POST.get("num_of_board_members").strip()
                member.save()
                messages.success(request, "Your Profile Updated Successfully", 'success')

            elif request.POST.get("form-name") == 'change-password-form':
                # change password form
                # 'password', 'new-password', 'verify-new-password']
                pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$"
                old_password = request.POST.get("password")
                new_password = request.POST.get("new-password")
                confirmation = request.POST.get("verify-new-password")
                checked = check_password(old_password, request.user.password)
                # check if the password is not empty
                if old_password:
                    # check if the old password is correct
                    if checked is True:
                        # check if the confirm password is matched
                        if confirmation == new_password:
                            searched = re.search(pattern, new_password)
                            if searched is not None:
                                hashed_password = make_password(new_password)
                                email = request.user.email
                                member.password = hashed_password
                                member.save()
                                update_session_auth_hash(request, member)
                                messages.success(request, "Your Password Updated Successfully!", 'success')
                            else:
                                messages.error(request, 'Password not match conditions!!', 'danger')
                        else:
                            messages.error(request, 'Confirmation Password not match!!', 'danger')

                    else:
                        messages.error(request, 'Your old password not correct!', 'danger')
                else:
                    messages.error(request, 'Old password is empty!', 'danger')

            return redirect(request.get_full_path())
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')


class ProfilePersonal(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        # cprint(self.request.user, 'blue')
        return True

    def get(self, request):
        try:
            member = Member.objects.get(email=request.user.email)
            return render(request, "members_app/profile/personal.html", context={"member": member})
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())

    def post(self, request):
        try:
            member = Member.objects.get(email=request.user.email)
            member.first_name = request.POST.get("first-name").strip()
            member.last_name = request.POST.get("last-name").strip()
            member.full_name = f'{request.POST.get("first-name").strip()} {request.POST.get("last-name").strip()}'
            member.email = request.POST.get("email").strip()
            member.phone = request.POST.get("phone").strip()
            member.save()
            messages.success(request, 'your info have been updated successfully!')
            return redirect(reverse('profile-personal'))

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')


class ProfileInformation(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        try:
            member = Member.objects.get(email=request.user.email)
            return render(request, "members_app/profile/information.html",
                          context={"member": member, 'annual_revenue': ANNUAL_REVENUE, 'org_types': ORGANIZATION_TYPES})
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())

    def post(self, request):
        try:
            member = Member.objects.get(email=request.user.email)
            # ['csrfmiddlewaretoken', 'org_name', 'org_website', 'organizationType', 'annualRevenue', 'job_title', 'total_staff', 'num_of_volunteer']
            member.org_name = request.POST.get("org_name").strip()
            member.org_website = request.POST.get("org_website").strip()
            if request.POST.get("org_type") != "Other":
                member.org_type = request.POST.get("org_type").strip()
            else:
                member.org_type = request.POST.get("other-org-type").strip()
            member.annual_revenue = request.POST.get("annualRevenue").strip()
            member.job_title = request.POST.get("job_title").strip()
            member.total_staff = request.POST.get("total_staff").strip()
            member.num_of_volunteer = request.POST.get("num_of_volunteer").strip()
            member.num_of_board_members = request.POST.get("num_of_board_members").strip()
            member.save()

            messages.success(request, 'your info have been updated successfully!')
            return redirect(reverse('profile-info'))

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')


class ProfileChangePassword(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        try:
            member = Member.objects.get(email=request.user.email)
            return render(request, "members_app/profile/change-password.html", context={"member": member})
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())

    def post(self, request):
        try:
            # ^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$
            import re
            member = Member.objects.get(email=request.user.email)
            # 'password', 'new-password', 'verify-new-password'
            if request.POST.get('password') == '':
                messages.error(request, 'Password is empty!!')
            elif request.POST.get("new-password") == "":
                messages.error(request, 'New Password is empty!!')
            elif request.POST.get("verify-new-password") == "":
                messages.error(request, 'You have to verify new password is empty!!')
            elif request.POST.get("verify-new-password") != request.POST.get("new-password"):
                messages.error(request, 'Password not verified or matched!!')
            else:
                if member.check_password(request.POST.get("password")) is True:

                    pattern = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$")
                    if pattern.match(request.POST.get('new-password')):
                        member.set_password(request.POST.get("new-password"))
                        member.save()
                        update_session_auth_hash(request, member)
                        messages.success(request, 'Your password has been updated!')
                    else:
                        messages.error(request, 'Your password not match password requirements!')

                else:
                    messages.error(request, 'Your old password is not correct!')
            return redirect(reverse('profile-change-password'))

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, 'There is errors!, try again latter')


class ProfileEmail(LoginRequiredMixin, View):
    # template_name = "members_app/profile/email.html"
    login_url = "login"

    def get(self, request):
        member = Member.objects.get(email=request.user.email)
        return render(request, "members_app/profile/email.html", context={"member": member})


class SubscriptionManageView(LoginRequiredMixin, View):
    # template_name = "members_app/profile/subscription.html"
    login_url = "login"

    def get(self, request):
        member = Member.objects.get(email=request.user.email)
        return render(request, "members_app/profile/subscription.html", context={"member": member})
