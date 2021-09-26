import traceback

from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.views.generic import (ListView, DetailView)
from django.shortcuts import (redirect, reverse)
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from termcolor import cprint

from predict_me.my_logger import log_exception
from users.models import Member
from predict_me.constants.countries import (ALL_COUNTRIES, ALL_STATS)
from predict_me.constants.vars import (ANNUAL_REVENUE, ORGANIZATION_TYPES)
from membership.helpers import get_member_total_charges


class UsersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "dash_users/list.html"
    model = Member
    login_url = "login"
    ordering = ['-date_joined']

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['avatars'] = (
            "assets/media/svg/avatars/001-boy.svg",
            "assets/media/svg/avatars/018-girl-9.svg",
            'assets/media/svg/avatars/047-girl-25.svg',
            "assets/media/svg/avatars/014-girl-7.svg",
        )
        # fetch all cities for all members from db
        cities = Member.objects.values_list("city", flat=True)
        context['all_countries'] = ALL_COUNTRIES
        context['all_stats'] = ALL_STATS
        context['org_types'] = ORGANIZATION_TYPES
        context['annual_revenue'] = ANNUAL_REVENUE
        context['cities'] = list(cities)
        return context


class UsersCreateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "dash_users/create.html"
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))


class UsersDetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = "dash_users/details.html"
    login_url = "login"
    model = Member

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_obj = context.get('member')
        stripe_charges = get_member_total_charges(member_obj)
        context['total_spent'] = stripe_charges.get("all_charges_amount")
        context['charges_sum'] = stripe_charges.get("charges_sum")
        context['all_countries'] = ALL_COUNTRIES
        context['all_stats'] = ALL_STATS
        context['annual_revenue'] = ANNUAL_REVENUE
        context['org_types'] = ORGANIZATION_TYPES
        return context


class UsersPendingView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "dash_users/list_pending.html"
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))


class FetchMemberDetailsView(APIView):
    """
    this view will fetch the info of the member

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # save_point = transaction.savepoint()

        try:
            member_data = request.data
            member_id = int(member_data.get("memberID"))
            member = Member.objects.get(pk=member_id)
            stripe_charges = get_member_total_charges(member)
            member_data_dict = member.get_member_info_as_dict
            member_data_dict['total_spent'] = stripe_charges.get('all_charges_amount')
            return JsonResponse(data={"member": member_data_dict}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return JsonResponse(data={'error_msg': 'Error when change crash status!!, try again later', 'status': 401},
                                status=401)


class DeleteMemberView(APIView):
    """
    this view will delete member from administrator dashboard

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # save_point = transaction.savepoint()

        try:
            member_data = request.data

            return JsonResponse(data={"member": "Delete member api view"}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            return JsonResponse(data={'error_msg': 'Error when change crash status!!, try again later', 'status': 401},
                                status=401)


# only for testing
def delete_members(request):
    all_members = Member.objects.all()
    cprint(len(all_members), 'magenta')

    for member in all_members:
        if member.is_superuser is False:
            if member.subscription.filter().first() is None:
                member.delete()
                cprint("Member has been deleted!", 'green')

    return HttpResponse("Test deleting members how has no subscription and memberships ")
