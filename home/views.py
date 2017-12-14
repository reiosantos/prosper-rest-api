import os
from datetime import date
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import Resolver404
from django.views import View
from django.views.decorators.http import require_GET, require_http_methods
from weasyprint import HTML

from config.prosper import COMPANY_NAME
from config.settings import REPORT_ROOT, MEDIA_URL
from finance.forms import InterestForm
from finance.models import Interest
from home.forms import ExpensesForm
from home.models import Expenses
from home.support.support_functions import save_details, save_interest, monthly_rate_today, \
    expected_contributions, cash_at_hand, all_contributions, all_loans, all_investments, \
    calculate_income_statement, get_user_contributions, get_user_investments, get_user_loans
from home.support.validators import generate_report_filename, RequiredFormset


@require_GET
def no_script(request):
    return render(request, 'error/no_script.html')


def custom_page_not_found(request):
    return render(request, 'error/404.html', status=404)


def custom_server_error(request):
    return render(request, 'error/500.html', status=500)


def custom_permission_denied(request):
    return render(request, 'error/403.html', status=403)


def custom_bad_request(request):
    return render(request, 'error/400.html', status=400)


@require_http_methods(['GET', 'POST'])
def index(request):

    if not request.user.user_type == "admin":
        return redirect('profile_page')

    error = {}
    message = None
    no_of_forms = 1

    monthly_rate, today, start_date, months_in_operation, form = monthly_rate_today()
    loan_rate = 0

    i_form = InterestForm()
    expenses_form = modelformset_factory(Expenses,
                                         ExpensesForm,
                                         extra=no_of_forms, can_order=False,
                                         can_delete=False, formset=RequiredFormset)

    admin_expenses_formset = expenses_form(queryset=Expenses.objects.all())

    if request.POST:
        interest = request.POST.get('hidden_interest', False)
        details = request.POST.get('hidden_details', False)

        if interest:
            save = save_interest(request, interest)
            if save['status']:
                message = 'Interest rate updated.'
            else:
                i_form = save['form']
                error['error'] = 'Failed to complete transaction.'
                error['form'] = 'interest'

        elif details:
            save = save_details(request, details)
            if save['status']:
                message = 'Update has been successful.'
            else:
                form = save['form']
                error['error'] = 'Failed to complete transaction.'
                error['form'] = 'details'
        else:
            # to handle expense formset submissions
            admin_expenses_formset = expenses_form(request.POST, request.FILES)
            if admin_expenses_formset.is_valid():
                Expenses.objects.all().delete()

                for form in admin_expenses_formset.forms:
                    if form.is_valid():
                        form.save()
                else:
                    admin_expenses_formset = expenses_form(queryset=Expenses.objects.all())

    ir = Interest.objects.all()
    if ir and ir.count() > 0:
        ir = ir[0]
        loan_rate = ir.interest
        i_form = InterestForm(instance=ir)

    total_membership, expected_total_contributions = expected_contributions(monthly_rate)
    banked_cash_at_hand, un_banked_cash_at_hand, expected_total_cash_at_hand, variance = cash_at_hand()

    return render(request, 'home/dashboard.html',
                  {
                      'title': "Admin Dashboard",
                      'no_search': True,
                      'form': form,
                      'i_form': i_form,
                      'expenses_forms': admin_expenses_formset,
                      'loan_rate': loan_rate,
                      'today': today,
                      'start_date': start_date,
                      'months_in_operation': months_in_operation,
                      'total_membership': total_membership,
                      'monthly_rate': monthly_rate,
                      'expected_total_contributions': expected_total_contributions,
                      'expected_total_cash_at_hand': expected_total_cash_at_hand,
                      'banked_cash_at_hand': banked_cash_at_hand,
                      'unbanked_cash_at_hand': un_banked_cash_at_hand,
                      'variance': variance,
                      'error': error,
                      'message': message,
                      'all_contributions': all_contributions(monthly_rate, today),
                      'all_loans': all_loans(),
                      'all_investments': all_investments(),
                      'income_statements': calculate_income_statement(),
                  })


class PrintFunction(View):

    def get(self, request, what=None):

        if not request.user.is_authenticated():
            return redirect('login_user')

        if not what:
            raise Resolver404('Not Found')

        if what == 'admin_dashboard':
            if not request.user.user_type == "admin":
                raise PermissionDenied('permission denied')
            # preparing report data
            loan_rate = Decimal(0)
            ir = Interest.objects.all()
            if ir and ir.count() > 0:
                ir = ir[0]
                loan_rate = ir.interest
            monthly_rate, today, start_date, months_in_operation, form = monthly_rate_today()
            total_membership, expected_total_contributions = expected_contributions(monthly_rate)
            banked_cash_at_hand, un_banked_cash_at_hand, expected_total_cash_at_hand, variance = cash_at_hand()
            expenses = Expenses.objects.all().order_by('-date')

            temp_vars = {'logo': os.path.join(MEDIA_URL, 'logo-web.png'),
                         'user': request.user, 'title': COMPANY_NAME,
                         'loan_rate': loan_rate,
                         'today': today,
                         'start_date': start_date,
                         'months_in_operation': months_in_operation,
                         'total_membership': total_membership,
                         'monthly_rate': monthly_rate,
                         'expected_total_contributions': expected_total_contributions,
                         'expected_total_cash_at_hand': expected_total_cash_at_hand,
                         'banked_cash_at_hand': banked_cash_at_hand,
                         'unbanked_cash_at_hand': un_banked_cash_at_hand,
                         'variance': variance,
                         'expenses': expenses,
                         'all_contributions': all_contributions(monthly=monthly_rate, today=today),
                         'all_loans': all_loans(),
                         'all_investments': all_investments(),
                         'income_statements': calculate_income_statement(),
                         }
            try:
                template = get_template('print/dashboard.html')
                out_put = template.render(temp_vars)

            except TemplateDoesNotExist:
                raise Resolver404('Admin Template Not Found')

        elif what == 'user_profile':

            # preparing report data
            today = date.today()
            contribution = get_user_contributions(request.user, today)
            investment = get_user_investments(request)
            loan = get_user_loans(request)

            temp_vars = {
                'logo': os.path.join(MEDIA_URL, 'logo-web.png'),
                'MEDIA_URL': MEDIA_URL,
                'user': request.user, 'title': COMPANY_NAME,
                'today': today,
                'contributions': contribution['contributions'],
                'summary': contribution['summary'],
                'i_manage': investment['i_manage'],
                'a_member': investment['a_member'],
                'others': investment['other'],
                'on_loan': loan['on_loan'],
                'on_pay': loan['on_pay'],
                'credit': loan['credit'],
            }
            try:
                template = get_template('print/user_profile.html')
                out_put = template.render(temp_vars)

            except TemplateDoesNotExist:
                raise Resolver404('User Template Not Found')

        else:
            raise Resolver404('URL Not Understood')

        try:
            name = '{0}.pdf'.format(generate_report_filename())
            HTML(string=out_put, base_url=request.build_absolute_uri()).write_pdf(os.path.join(REPORT_ROOT, name))

            fs = FileSystemStorage(REPORT_ROOT)

            with fs.open(name) as pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename={0}.pdf'.format(name)
                return response

        except Exception as e:
            raise Resolver404('No preview page found ')
