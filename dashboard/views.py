from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, reverse



class DashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy("login")
    template_name = "dashboard/dashboard.html"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))


