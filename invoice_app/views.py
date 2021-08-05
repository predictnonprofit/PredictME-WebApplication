import traceback
from .models import (Invoice, Transactions)
from django.views.generic import (TemplateView, View)
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from termcolor import cprint
from xhtml2pdf import pisa
from weasyprint import HTML, CSS
from django.db import IntegrityError
from django.shortcuts import (reverse, redirect, render)
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
import stripe

from predict_me.my_logger import log_exception


class GrabMemberInvoices(APIView):
    """
        ### Developments only ###
        API View to grab invoices of the user

        * Requires token authentication.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            import time
            import datetime
            request_data = request.POST
            member = request.user
            member_subscription = member.member_subscription.get()
            start_date = request_data.get("startDate")
            end_date = request_data.get("endDate")
            invoices_count = 0
            all_invoices = list()

            # validate if start date or end date are empty
            if (start_date == "") and (end_date == ''):
                return JsonResponse(data={"msg": "Start Date and End date are Empty!", 'status': "Error"}, status=200)
            else:
                # stripe_invoices = stripe.Invoice.list(customer=member_subscription.member_id.stripe_customer_id)
                # cprint(stripe_invoices['data'][0]['created'], 'blue')
                # cprint(stripe_invoices['data'][1]['created'], 'blue')
                # cprint(len(stripe_invoices), 'blue')
                start_time = time.mktime(datetime.datetime.strptime(start_date, "%m/%d/%Y").timetuple())
                end_time = time.mktime(datetime.datetime.strptime(end_date, "%m/%d/%Y").timetuple())
                stripe_invoices = stripe.Invoice.list(customer=member_subscription.member_id.stripe_customer_id,
                                                      created={
                                                          'gte': int(start_time),
                                                          "lte": int(end_time)
                                                      })
                # cprint(stripe_invoices, 'red')
                cprint(len(stripe_invoices), 'blue')
                invoices_count = len(stripe_invoices)

                for invoice in stripe_invoices:
                    # save the invoice the db
                    try:
                        invoice_obj = Invoice()
                        invoice_obj.member = request.user
                        invoice_obj.invoice_stripe_id = invoice['id']
                        invoice_obj.invoice_pdf_url = invoice.get("invoice_pdf")
                        invoice_obj.save()
                    except IntegrityError as ier:
                        # check if the unique constraint
                        if "UNIQUE constraint" in ier.args[0]:
                            pass
                    all_invoices.append({
                        # 'id': invoice['id'],
                        "customer": request.user.full_name,
                        'created': datetime.datetime.fromtimestamp(invoice.get("created")).strftime('%m/%d/%Y'),
                        "period_start": datetime.datetime.fromtimestamp(invoice.get('period_start')).strftime(
                            '%m/%d/%Y'),
                        "period_end": datetime.datetime.fromtimestamp(invoice.get('period_end')).strftime('%m/%d/%Y'),
                        'status': invoice.get('status'),
                        'amount_due': float(invoice.get('amount_due')),
                        'amount_remaining': float(invoice.get('amount_remaining')),
                        'amount_paid': float(invoice.get('amount_paid')),
                        "invoice_pdf": invoice.get('invoice_pdf'),
                        "due_date": invoice.get('due_date')
                    })

            return JsonResponse(data={'invoices_count': invoices_count, "invoices": all_invoices}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)


class GrabMemberTransactions(APIView):
    """
        ### Developments only ###
        API View to grab all transactions of the user

        * Requires token authentication.
        """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        try:
            import time
            import datetime
            request_data = request.POST
            member = request.user
            member_subscription = member.member_subscription.get()
            start_date = request_data.get("startDate")
            end_date = request_data.get("endDate")
            trans_count = 0
            all_trans = list()

            # validate if start date or end date are empty
            if (start_date == "") and (end_date == ''):
                return JsonResponse(data={"msg": "Start Date and End date are Empty!", 'status': "Error"}, status=200)
            else:
                start_time = time.mktime(datetime.datetime.strptime(start_date, "%m/%d/%Y").timetuple())
                end_time = time.mktime(datetime.datetime.strptime(end_date, "%m/%d/%Y").timetuple())
                stripe_trans = stripe.Charge.list(customer=member_subscription.member_id.stripe_customer_id)
                # cprint(stripe_trans, 'red')
                cprint(len(stripe_trans['data']), 'blue')
                trans_count = len(stripe_trans)

                for trans in stripe_trans['data']:
                    # save the transaction to db
                    try:
                        trans_obj = Transactions()
                        trans_obj.trans_stripe_id = trans.get('id')
                        trans_obj.member = request.user
                        trans_obj.invoice_stripe_id = trans.get("invoice")
                        trans_obj.receipt_pdf_url = trans.get("receipt_url")
                        trans_obj.save()
                    except IntegrityError as ier:
                        # check if the unique constraint
                        if "UNIQUE constraint" in ier.args[0]:
                            pass

                    # cprint(trans, 'green')
                    all_trans.append({
                        # 'id': trans.get('id'),
                        "customer": request.user.full_name,
                        'created': datetime.datetime.fromtimestamp(trans.get("created")).strftime('%m/%d/%Y'),
                        "paid": trans.get("paid"),
                        "card": trans.get("payment_method_details").get("card").get(
                            "network") + " - " + "************" + trans.get("payment_method_details").get("card").get(
                            "last4"),
                        'captured': trans.get('captured'),
                        'amount': trans.get("amount"),
                        "receipt_url": trans.get('receipt_url'),
                    })

            return JsonResponse(data={'trans_count': trans_count, "trans": all_trans}, status=200)

        except Exception as ex:
            cprint(traceback.format_exc(), 'red')
            cprint(str(ex), 'red')
            log_exception(ex)


class InvoiceDetailsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "invoice_app/detail.html"
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))


class InvoiceListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "invoice_app/list.html"
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))


class InvCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "login"

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse('profile-overview'))

    def get(self, request):
        return render(request, "invoice_app/create.html")

    def post(self, request):
        print(request.POST)
        return render(request, "invoice_app/create.html")


# def generate_printable_pdf(template_src, invoice_context_data={}):
#     template = get_template(template_src)
#     html = template.render(invoice_context_data)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type="application/pdf")
#
#     return None

def pdf_generation(request):
    html_template = get_template('templates/home_page.html')
    pdf_file = HTML(string=html_template).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="home_page.pdf"'
    return response


class InvoicePrintView(View):

    def get(self, request, *args, **kwargs):
        html_template = get_template('invoice_app/inc/invoice_template.html')
        pdf_file = HTML(string=html_template).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="INVOICE #25.pdf"'
        return response
