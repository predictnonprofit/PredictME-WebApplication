import traceback

from django.http import JsonResponse
from django.shortcuts import (redirect, reverse)
from django.views.generic import (TemplateView, DetailView)
from django.views.generic import ListView
from django.contrib.auth.mixins import (UserPassesTestMixin, LoginRequiredMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from termcolor import cprint
from django.contrib import messages
from django.urls import resolve

from predict_me.my_logger import log_exception
from .forms import CrashReportForm
from .models import CrashReport


class CrashReportsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "crash_reporting/list.html"
    login_url = "login"
    model = CrashReport
    ordering = ['-created_date']

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))


class CrashReportsDetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = "crash_reporting/details.html"
    login_url = "login"
    model = CrashReport

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context.get("object")
        crash_status = (
            ("not_fixed", "Not Fixed"),
            ("fixed", "Fixed"),
            ("in_progress", "In Progress"),
        )
        context['crash_status'] = crash_status
        obj.is_seen = True
        obj.save()
        return context

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))


class ReportCrashView(TemplateView):
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        try:
            current_url = resolve(request.POST.get('crash_url')).url_name  # this to redirect the user to the same page
            crash_form = CrashReportForm(data=request.POST, files=request.FILES, request=request)
            # check if crash form is valid
            if crash_form.is_valid():
                crash_model = crash_form.save()
                messages.success(request, 'Crash report submitted successfully!', 'success')
            else:
                cprint(crash_form.errors, "red")
                messages.error(request, f"{crash_form.errors}", 'danger')
            return redirect(reverse(current_url))

        except Exception as ex:
            log_exception(traceback.format_exc())
            cprint(traceback.format_exc(), "red")


class ChangeCrashReportStatusView(APIView):
    """
    this view change the status of the crash report

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, *args, **kwargs):
        # save_point = transaction.savepoint()

        try:
            crash_id = int(request.data.get("crashID"))
            crash_status = request.data.get("crashStatus")
            crash_obj = CrashReport.objects.get(pk=crash_id)
            crash_obj.crash_status = crash_status
            # check if the crash status is fixed
            if crash_status == 'fixed':
                crash_obj.is_solved = True
            else:
                crash_obj.is_solved = False
            crash_obj.save()
            return JsonResponse(data={"msg": "Change status", 'status': 200}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return JsonResponse(data={'error_msg': 'Error when change crash status!!, try again later', 'status': 401},
                                status=401)
