from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import messages
from django.views.generic import TemplateView
from django.views import View
from membership.models import (Membership, Subscription)
from data_handler.models import (DataFile)
from termcolor import cprint
import stripe
import os
from django.conf import settings

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# Create your views here.

class AboutView(TemplateView):
    template_name = 'predict_me/about.html'


class ContactView(TemplateView):
    template_name = 'predict_me/contact.html'


class FAQView(TemplateView):
    template_name = 'predict_me/faq.html'


class PricingView(View):

    def get(self, request):
        return render(request, "predict_me/pricing.html")

    def post(self, request):
        member_type = request.POST['type']
        # cprint(request.POST, 'cyan')
        member = request.user
        # print(member.full_name)
        # membership2 = Membership.objects.filter(Q(range_label=member_type) & Q(parent='starter')).first()
        membership = Membership.objects.get(slug=member_type)
        member_data_file = DataFile.objects.get(member=member)
        # print(membership)
        # user_membership = UserMembership.objects.get(member=member)
        subscription = Subscription.objects.get(member_id=member)
        subscription.stripe_plan_id = membership
        # cprint(subscription.stripe_plan_id, "blue")
        # cprint(membership.slug, "green")
        member_data_file.allowed_records_count = membership.allowed_records_count

        subscription.save()
        member_data_file.save()
        # print(user_membership.membership)

        # messages.success(request, f"The plan you selected is {membership.membership_type} plan")
        return redirect(reverse("checkout"))


class ModelDescView(TemplateView):
    template_name = 'predict_me/model_description.html'


class LandPageView(TemplateView):
    template_name = 'predict_me/land_page.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'predict_me/privacy_policy.html'


class TermsView(TemplateView):
    template_name = 'predict_me/terms.html'


def error_503(request):
    return render(request, "predict_me/errors/503.html")
