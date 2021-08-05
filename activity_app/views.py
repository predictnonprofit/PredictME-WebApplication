from django.shortcuts import (redirect, reverse)
from django.views.generic import TemplateView
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)


class ListActivitiesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "activity_app/list.html"
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))
