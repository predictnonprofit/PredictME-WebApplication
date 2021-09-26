import os
import traceback

import stripe
from django.db import transaction
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from termcolor import cprint
from django.contrib import messages
from membership.models import Membership
from predict_me.my_logger import log_exception

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# Create your views here.

class AboutView(TemplateView):
    template_name = 'predict_me/about.html'


class ContactView(TemplateView):
    template_name = 'predict_me/contact.html'


class FAQView(TemplateView):
    template_name = 'predict_me/faq.html'


class PricingView(TemplateView):
    template_name = "predict_me/pricing.html"

    @transaction.atomic
    def post(self, request):
        try:
            membership_slug = request.POST.get("type")
            member = request.user
            subscription = member.subscription.select_for_update().get()
            membership = Membership.objects.get(slug=membership_slug)
            member_data_file = member.member_data_file.select_for_update().get()

            subscription.membership = membership
            # cprint(subscription.stripe_plan_id, "blue")
            # cprint(membership.slug, "green")
            member_data_file.allowed_records_count = membership.allowed_records_count

            subscription.save()
            member_data_file.save()
            # print(user_membership.membership)
            membership_name = membership.get_membership_type_display()
            messages.success(request, f"You select {membership_name} membership successfully!")
            return redirect(reverse("checkout"))
        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            log_exception(traceback.format_exc())
            messages.error(request, "Error in pricing!!")
            return redirect(reverse("pricing"))


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
