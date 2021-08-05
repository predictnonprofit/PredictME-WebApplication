from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from users.models import Member
from django.shortcuts import render, redirect, reverse


class AdminProfileOverview(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        member = Member.objects.get(email=request.user.email)
        return render(request, "admin_profile/overview.html", context={"member": member})


class AdminProfilePersonal(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        member = Member.objects.get(email=request.user.email)
        return render(request, "admin_profile/personal.html", context={"member": member})


class AdminProfileInformation(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        member = Member.objects.get(email=request.user.email)
        return render(request, "admin_profile/information.html", context={"member": member})


class AdminProfileChangePassword(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        member = Member.objects.get(email=request.user.email)
        return render(request, "admin_profile/change-password.html", context={"member": member})


