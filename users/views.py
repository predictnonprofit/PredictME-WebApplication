from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from .helpers import *
from collections import defaultdict
from .models import Member
from django.http import HttpResponseRedirect
from django.core.cache import cache
from termcolor import cprint
from django.contrib.sites.shortcuts import get_current_site
import traceback
from predict_me.my_logger import (log_exception, log_info)


class MembersLoginView(TemplateView):
    def get(self, request, *args, **kwargs):
        cache.set('next', request.GET.get('next', None))
        return render(request, "users/auth/login.html")

    def post(self, request, *args, **kwargs):
        try:
            input_errors = dict()
            email = request.POST['email'].strip()
            password = request.POST['password']

            # validate user inputs
            if (email == '') or (email is None):
                input_errors['email'] = "Email Address Required!"

            if (password == '') or (password is None):
                input_errors['password'] = "Password Required!"

            # check if there any errors in user inputs
            if input_errors:
                return render(request, "users/auth/login.html", context={"errors": input_errors, "email": email})

            else:
                # in case no errors
                member = authenticate(request, email=email, password=password)
                if member is not None:
                    login(request, member)

                    if member.email == "admin@admin.com" or member.email == "admin2@email.com":
                        return redirect(reverse("dashboard-home"))
                    else:
                        next_url = cache.get('next')
                        if next_url and 'profile/data' in next_url:
                            cache.delete('next')
                            return HttpResponseRedirect(next_url)
                        return redirect(reverse("profile-overview"))
                else:
                    # user credentials not correct
                    input_errors['login_error'] = "credentials not correct, please try again!"
                    return render(request, "users/auth/login.html",
                                  context={"login_error": input_errors, "email": email})
        except Exception as ex:
            cprint(traceback.format_exc(), 'red', 'on_grey')
            log_exception(traceback.format_exc())
            return render(request, "users/auth/login.html",
                          context={"login_error": str(ex), "email": email})


def register_view(request):
    if request.method == "POST":
        INPUTS_DATA = {}  # this will hold all input values
        INPUTS_ERRORS = defaultdict(list)  # this will hold all errors of every input, if empty then good to go
        INPUTS_DATA['first_name'] = request.POST.get('first_name')
        INPUTS_DATA['last_name'] = request.POST.get('last_name')
        INPUTS_DATA['full_name'] = f"{request.POST.get('first_name')} {request.POST.get('last_name')}"
        INPUTS_DATA['email'] = request.POST.get("email")
        INPUTS_DATA['phone'] = request.POST.get("phone")
        INPUTS_DATA['street_address'] = request.POST.get("street_address")
        INPUTS_DATA['org_name'] = request.POST.get("org_name")
        INPUTS_DATA['country'] = request.POST.get("country")
        INPUTS_DATA['city'] = request.POST.get("city")
        INPUTS_DATA['state'] = request.POST.get("state")
        INPUTS_DATA['zip'] = request.POST.get("zip")
        INPUTS_DATA['job_title'] = request.POST.get("job_title")
        INPUTS_DATA['annual_revenue'] = request.POST.get("annual_revenue")
        INPUTS_DATA['org_type'] = request.POST.get('org_type')
        INPUTS_DATA['other_org_type'] = request.POST.get("other_org_type")
        INPUTS_DATA[
            'final_org_type'] = None  # this will be the org_type if user decided it from menu or enter custom type
        INPUTS_DATA['org_website'] = request.POST.get("org_website")
        INPUTS_DATA['total_staff'] = request.POST.get("total_staff")
        INPUTS_DATA['number_volunteer'] = request.POST.get("number_volunteer")
        INPUTS_DATA['number_board_members'] = request.POST.get("number_board_members")
        INPUTS_DATA['accepted_privacy_terms'] = request.POST.get("accepted_privacy_terms")

        # first, validate the inputs
        if not input_required(INPUTS_DATA['first_name']):
            INPUTS_ERRORS['first_name'].append("First Name Required!")
        else:
            if not validate_name(INPUTS_DATA['first_name']):
                INPUTS_ERRORS['first_name'].append("First name not valid!")

        # last name validate
        if not input_required(INPUTS_DATA['last_name']):
            INPUTS_ERRORS['last_name'].append("Last Name Required!")
        else:
            if not validate_name(INPUTS_DATA['last_name']):
                INPUTS_ERRORS['last_name'].append("Last name not valid!")

        # email validate
        if not input_required(INPUTS_DATA['email']):
            INPUTS_ERRORS['email'].append("Email address Required!")
        else:
            if not validate_email(INPUTS_DATA['email']):
                INPUTS_ERRORS['email'].append("Email address not valid!")

        # phone validate
        if not validate_phone(INPUTS_DATA['phone']):
            INPUTS_ERRORS['phone'].append("Phone number not valid!")

        # street address validate
        if not input_required(INPUTS_DATA['street_address']):
            INPUTS_ERRORS['street_address'].append("Street address Required!")
        else:
            if not validate_street_address(INPUTS_DATA['street_address']):
                INPUTS_ERRORS['street_address'].append("Street address not valid!")

        # org name validate
        if not input_required(INPUTS_DATA['org_name']):
            INPUTS_ERRORS['org_name'].append("Organization Name Required!")
        else:
            if not validate_alphnum(INPUTS_DATA['org_name']):
                INPUTS_ERRORS['org_name'].append("Organization Name not valid!")

        # city validate
        if INPUTS_DATA['city'] != "":
            if not validate_city(INPUTS_DATA['city']):
                INPUTS_ERRORS['city'].append("City Name not valid!")

        # state validate
        if INPUTS_DATA['state'] == 0 or INPUTS_DATA['city'] == "0":
            INPUTS_ERRORS['state'].append("Please choose state!")

        # annual_revenue validate
        if INPUTS_DATA['annual_revenue'] is None or INPUTS_DATA['annual_revenue'] == "":
            INPUTS_ERRORS['annual_revenue'].append("choose your annual revenue!")

        # zip validate
        if not input_required(INPUTS_DATA['zip']):
            INPUTS_ERRORS['zip'].append("Zip code Required!")
        else:
            if not validate_zip(INPUTS_DATA['zip']):
                INPUTS_ERRORS['zip'].append("Zip code not valid!")

        # check custom other_org_type
        if INPUTS_DATA['org_type'] is None or INPUTS_DATA['org_type'] == "":
            INPUTS_ERRORS['org_type'].append("Organization type required!")

        # check if user accept the privacy term checkbox
        if INPUTS_DATA['accepted_privacy_terms'] != "1":
            INPUTS_ERRORS['accepted_privacy_terms'].append("You must accept our privacy terms!")

        # check all errors
        if INPUTS_ERRORS:

            return render(request, "users/auth/register.html",
                          context={"input_errors": INPUTS_ERRORS, "input_data": INPUTS_DATA})
        else:
            # here if there is any errors, all validation applied and there are no invalid data

            # save the new member to db
            new_member = Member()
            new_member.email = INPUTS_DATA['email'].strip()
            new_member.first_name = INPUTS_DATA['first_name'].strip()
            new_member.last_name = INPUTS_DATA['last_name'].strip()
            new_member.full_name = INPUTS_DATA['full_name'].strip()
            new_member.phone = INPUTS_DATA['phone'].strip() if INPUTS_DATA['phone'] else ""
            new_member.country = INPUTS_DATA['country'].strip()
            new_member.state = INPUTS_DATA['state'].strip() if INPUTS_DATA['state'] else ""
            new_member.city = INPUTS_DATA['city'].strip()
            new_member.street_address = INPUTS_DATA['street_address'].strip()
            new_member.zip_code = INPUTS_DATA['zip'].strip()
            new_member.org_name = INPUTS_DATA['org_name'].strip()
            new_member.job_title = INPUTS_DATA['job_title'].strip() if INPUTS_DATA['job_title'] else ""
            new_member.org_website = INPUTS_DATA['org_website'].strip() if INPUTS_DATA['org_website'] else ""

            if INPUTS_DATA['org_type'] == 'Other':
                new_member.org_type = "Other"
                new_member.other_org_type = INPUTS_DATA['other_org_type'].strip()
            else:
                new_member.org_type = INPUTS_DATA['org_type'].strip()

            new_member.annual_revenue = INPUTS_DATA['annual_revenue'].strip()
            new_member.total_staff = float(INPUTS_DATA['total_staff'].strip()) if INPUTS_DATA['total_staff'] else float(
                0.0)
            new_member.num_of_board_members = INPUTS_DATA['number_board_members'].strip() if INPUTS_DATA[
                'number_board_members'] else ""
            new_member.num_of_volunteer = INPUTS_DATA['number_volunteer'].strip() if INPUTS_DATA[
                'number_volunteer'] else ""
            new_member.status = "unverified"
            new_member.ip_address = get_member_ip_address(request)
            new_member.save()
            # print("New member has been saved!")
            member_activate_uid = urlsafe_base64_encode(force_bytes(new_member.pk))
            member_activate_token = account_activation_token.make_token(new_member)
            # print(f"Member Token:->  {member_activate_token} ")
            new_member.member_register_token = member_activate_token
            new_member.save()

            # send verification code to member email
            current_site = get_current_site(request)

            full_name = f"{INPUTS_DATA['full_name']}"
            email_subject = "Active Your Account"
            message = render_to_string("users/inc/confirm_email.html", {
                "user": new_member,
                "domain": current_site,
                'uid': member_activate_uid,
                'token': member_activate_token,
                'full_name': full_name,
            })
            email_to = INPUTS_DATA['email']
            email = EmailMessage(email_subject, message, to=[email_to, ])
            email.from_email = "Predict ME contact@predictme.com"
            email.content_subtype = "html"  # render html good in inbox
            email.send()
            print(f'Verification code Sent to {email_to}')
            messages.success(request, f"Your verification code has sent to your email {INPUTS_DATA['email']}")
            return redirect(reverse("users_verify"))

    return render(request, "users/auth/register.html")


class CompleteRegister(View):
    def get(self, request):

        member = Member.objects.get(email=request.session.get("MEMAIL"))
        return render(request, "users/inc/complete_register.html", context={"member": member})

    def post(self, request):

        # all_errrors = defaultdict(list)
        all_errors = dict()
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")
        # validate password with it is confirm
        if password == "" or password is None:
            # all_errors['password'].append("Password confirmation required!")
            all_errors['password'] = 'Password required!'
            messages.error(request, 'Password required!', 'danger')
        if confirm == "" or confirm is None:
            # all_errors['confirm'].append("Password confirmation required!")
            all_errors['confirm'] = 'Password confirmation required!'
            messages.error(request, 'Password confirmation required!', 'danger')

        if confirm != password:
            # all_errors['confirm'].append("Password confirmation not match the password!")
            all_errors['confirm'] = 'Password confirmation not match the password!'
            messages.error(request, 'Password confirmation not match the password!', 'danger')

        if all_errors:
            return redirect('register-complete')
        else:
            # make the password validation according what in the documentation
            clean_password = validate_password(password)
            member = Member.objects.get(email=request.session.get("MEMAIL"))
            # return HttpResponse(member)
            member.set_password(password)
            member.save()
            login_member = authenticate(request, email=member.email, password=password)
            if login_member is not None:
                login(request, login_member)
            # if all password requirement ok, redirect to pricing page
            return redirect(reverse("pricing"))


class PendingUserView(TemplateView):
    template_name = "users/inc/pending.html"


class CancelUserView(TemplateView):
    template_name = "users/inc/cancel.html"


class VerifyAccountView(TemplateView):
    template_name = "users/inc/verify.html"


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        member = Member.objects.get(pk=uid)
        print(member)
    except(TypeError, ValueError, OverflowError, Member.DoesNotExist):
        member = None
    if member is not None and account_activation_token.check_token(member, token):
        member.is_active = True
        member.status = "pending"
        request.session['MEMAIL'] = member.email
        # set cookie of new member
        # if not request.COOKIES.get('MEMAIL'):
        #     response = HttpResponse("Account Activate!")
        #     response.set_cookie("MEMAIL", member.email)

        member.save()
        messages.success(request, 'Congratulation your account is active!', 'success')
        return redirect(reverse("register-complete"))
        # return HttpResponse('Your account has been activate successfully')
    else:
        return HttpResponse('Activation link is invalid!')


# log out
def logout_view(request):
    logout(request)
    return redirect("land-page")


# social_authentication views
class GoogleAuthenticationView(TemplateView):
    template_name = "users/social_accounts/google.html"
