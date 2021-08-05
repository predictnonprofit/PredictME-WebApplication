from django.shortcuts import (render, reverse, get_object_or_404)
from django.views.generic import (TemplateView, FormView, UpdateView, DetailView)
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import FormMixin
from .models import CompanySettings
# from django.views.generic.edit import (UpdateView)
from .forms import CompanySettingsForm
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy


class CompanySettingsView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, FormMixin, DetailView):
    template_name = "site_settings/settings.html"
    form_class = CompanySettingsForm
    success_url = reverse_lazy('settings-company')
    model = CompanySettings
    success_message = "Company information updated!"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get_object(self):
        return get_object_or_404(CompanySettings, slug="company")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # print(form.cleaned_data)
        print(form.cleaned_data.get("status"))
        if form.is_valid():
            company_settings = CompanySettings.objects.get(slug="company")
            company_settings.name = form.cleaned_data.get("name")
            company_settings.email = form.cleaned_data.get("email")
            company_settings.phone = form.cleaned_data.get("phone")
            company_settings.logo = form.cleaned_data.get("logo")
            company_settings.description = form.cleaned_data.get("description")
            company_settings.keywords = form.cleaned_data.get("keywords")
            company_settings.country = form.cleaned_data.get("country")
            company_settings.city = form.cleaned_data.get("city")
            company_settings.admin_name = form.cleaned_data.get("admin_name")
            company_settings.admin_email = form.cleaned_data.get("admin_email")
            company_settings.status = form.cleaned_data.get("status")
            company_settings.close_msg = form.cleaned_data.get("close_msg")
            company_settings.save()

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class AboutSettingsView(TemplateView):
    template_name = "site_settings/about.html"


class PlansSettingsView(TemplateView):
    template_name = "site_settings/plans.html"
