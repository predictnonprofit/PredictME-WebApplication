from django.views.generic import TemplateView
from django.shortcuts import (reverse, redirect, render)
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)

# Create your views here.


class DataHandlerManageListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "data_handler_admin/list.html"
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))


class DataHandlerManageDetailsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "data_handler_admin/details.html"
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))