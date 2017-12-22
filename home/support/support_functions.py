from collections import OrderedDict
from datetime import date, datetime

import os
from dateutil import relativedelta

from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import Resolver404
from django.utils import timezone
from django.views import View

import django_excel as excel

from weasyprint import HTML
from xhtml2pdf import pisa

from config import settings
from config.prosper import COMPANY_NAME
from config.settings import REPORT_ROOT, MEDIA_URL
from finance.forms import InterestForm
from finance.models import Interest, Investment, Contribution, Loan, LoanPayment
from home.forms import DetailsForm
from home.models import ClubDetails, Expenses
from home.support.validators import generate_report_filename
from users.models import User


my_css = """
    @page {
        size: letter portrait;
        margin: 2cm;
    }
    img.logo {
        vertical-align: middle;
        border: 0;
        zoom: 20%;
    }
    body{
        font-family: 'Courier New', FreeMono, Courier, monospace;
        width: 100%;
        clear: both;
        padding: 10px;
        font-size: 12px;
    }
    table{
        margin-bottom: 20px;
        height: auto;
        width: 100%;
    }
    .no-top-border tr{
        margin-bottom: 10px;
        margin-top: 2cm;
    }
        table:not('.no-top-border') {
            border-top: 1px solid;
        }
        td{
            vertical-align: top;
            padding: 3px !important;
            border: 0;
            /*height: 100%;*/
        }
        fieldset{
            margin-bottom: 20px;
        }
        table.dashboard-tables{
            text-align: right;
        }
        .table-striped tbody tr:nth-child(odd) td,
        .table-striped tbody tr:nth-child(odd) th {
            background-color: #ececec;
        }
        .table-bordered {
            border: 1px solid #ddd;
        }
        .table-bordered > thead > tr > th,
        .table-bordered > tbody > tr > th,
        .table-bordered > tfoot > tr > th,
        .table-bordered > thead > tr > td,
        .table-bordered > tbody > tr > td,
        .table-bordered > tr > td,
        .table-bordered > tr > th,
        .table-bordered > tfoot > tr > td {
          border: 1px solid #ddd;
        }
        .table-bordered > thead > tr > th,
        .table-bordered > thead > th,
        .table-bordered > thead > td,
        .table-bordered > thead > tr > td {
          border-bottom-width: 2px;
        }
        table.dashboard-tables.contributions tbody tr:last-child{
            background: rgba(232,232,232,0.31);
            font-weight: bolder;
            text-align: right;
            border-top: 2px solid black !important;
        }
        tr, td{
        border-width: 1px;
        border-style: solid;
        }
    """


def user_time_passed(user):
    time_passed = relativedelta.relativedelta(timezone.now(), user.date_joined)

    months_passed = 0
    if time_passed.years and time_passed.months:
        months_passed = (time_passed.years * 12) + time_passed.months
        if time_passed.days:
            months_passed += 1
    elif time_passed.years and not time_passed.months:
        months_passed = (time_passed.years * 12)
        if time_passed.days:
            months_passed += 1
    elif time_passed.months and not time_passed.years:
        months_passed = time_passed.months
        if time_passed.days:
            months_passed += 1
    elif not time_passed.months and not time_passed.years:
        if time_passed.days:
            num = Contribution.objects.filter(user=user).annotate(month=TruncMonth('contribution_date')) \
                .values('month').annotate(num=Count('month')).order_by('month')
            if num:
                months_passed = num.count()
                if num[months_passed - 1]['month'].year == timezone.now().year and num[months_passed - 1][
                    'month'].month < \
                        timezone.now().month:
                    months_passed += 1
            else:
                months_passed += 1
        elif time_passed.hours or time_passed.minutes and not time_passed.days:
            months_passed += 1

    return months_passed, time_passed


def get_user_contributions(user, today=date.today()):
    """
    #contributions
    """
    try:
        monthly = ClubDetails.objects.all()
        if monthly:
            monthly = monthly[0].monthly_contribution
        else:
            monthly = 0
    except ClubDetails.DoesNotExist:
        monthly = 0

    this_month = Contribution.objects.filter(user=user, contribution_date__month=today.month).aggregate(
        Sum('total'))
    if not this_month['total__sum']:
        this_month['total__sum'] = 0

    balance = Decimal(monthly - this_month['total__sum'])
    if balance.as_tuple().sign == 1:
        balance = 0

    months_passed, time_passed = user_time_passed(user)
    expected = monthly * months_passed

    ever_made = Contribution.objects.filter(user=user).aggregate(Sum('total'))
    if not ever_made['total__sum']:
        ever_made['total__sum'] = 0

    excess = Decimal(ever_made['total__sum'] - expected)
    if excess.as_tuple().sign == 1:
        excess = 0

    total_b = Contribution.objects.filter(user=user).annotate(month=TruncMonth('contribution_date')) \
        .values('month').annotate(paid=Sum('total')).order_by('-month')

    total_balance = Decimal(0)
    for total in total_b:
        p = total['paid']
        y = total['month'].year
        m = total['month'].month

        if y == today.year and m == today.month:
            continue

        if total_balance.as_tuple().sign == 1:
            total_balance += 0
        else:
            total_balance += Decimal(monthly - p)
    else:
        total_balance += balance

    if not time_passed.years and not time_passed.months and not time_passed.days:
        time_since = str(time_passed.hours) + ' hour(s), and ' + str(time_passed.minutes) + \
                     ' minutes since you joined the group!!'
    elif not time_passed.years and not time_passed.months:
        time_since = str(time_passed.days) + ' day(s), since you joined the group!!'
    elif not time_passed.years:
        time_since = str(time_passed.months) + ' month(s) and ' + str(time_passed.days) + \
                     ' day(s), since you joined the group!!'
    elif time_passed.years:
        time_since = str(time_passed.years) + ' year(s), ' + str(time_passed.months) + ' month(s) and ' + str(
            time_passed.days) + ' day(s), since you joined the group!!'
    else:
        time_since = ''

    contributions = Contribution.objects.filter(user=user).order_by('-contribution_date')

    summary = {
        'monthly': monthly,
        'time_since': time_since,
        'this_month': this_month['total__sum'],
        'ever_made': ever_made['total__sum'],
        'expected': expected,
        'balance': balance,
        'total_balance': total_balance,
        'excess': excess
    }

    return {
        'contributions': contributions,
        'summary': summary
    }


def get_user_investments(request):
    i_manage = Investment.objects.filter(project_manager=request.user, project_status='in_progress')
    a_member = Investment.objects.filter(Q(project_status='in_progress') &
                                         Q(project_team=request.user) &
                                         ~Q(project_manager=request.user))
    other = Investment.objects.filter(~Q(project_team=request.user) &
                                      ~Q(project_manager=request.user))
    return {
        'i_manage': i_manage,
        'a_member': a_member,
        'other': other,
    }


def get_user_loans(request):
    loan = Loan.objects.filter(user=request.user, loan_status='running')
    credit = None
    if loan:
        on_loan = loan[0]
        on_pay = LoanPayment.objects.filter(loan=on_loan)
        if not on_pay:
            on_pay = None
    else:
        loans = Loan.objects.filter(user=request.user).order_by('loan_date')
        if loans and len(loans) > 0:
            credit = 0
            for loan in loans:
                if loan.outstanding_balance < 0:
                    credit += -1 * loan.outstanding_balance
        on_pay = None
        on_loan = None

    return {
        'on_loan': on_loan,
        'on_pay': on_pay,
        'credit': credit
    }


def calculate_user_expected_amount(user=None, monthly=0):
    if not user:
        return 0
    months_passed, time_passed = user_time_passed(user)
    expected = monthly * months_passed
    return expected


def monthly_rate_today():
    dt = ClubDetails.objects.all()

    today = date.today()
    start_date = today
    monthly_rate = 0
    months_in_operation = 0
    form = DetailsForm()

    if dt and dt.count() > 0:
        dt = dt[0]
        start_date = dt.start_date
        monthly_rate = dt.monthly_contribution
        months_passed = relativedelta.relativedelta(timezone.now(), start_date)
        if months_passed.years:
            months_in_operation = months_passed.years * 12
        if months_passed.months:
            months_in_operation += months_passed.months

        form = DetailsForm(instance=dt)

    return monthly_rate, today, start_date, months_in_operation, form


def expected_contributions(monthly_rate=0):
    expected_total_contributions = Decimal(0)
    total_membership = 0

    u = User.objects.all()
    if u:
        total_membership = u.count()
        for user in u:
            expected_total_contributions += calculate_user_expected_amount(user, monthly_rate)

    return total_membership, expected_total_contributions


def save_interest(request, hid=None):
    try:
        hid = int(hid)
    except TypeError:
        hid = None
    except ValueError:
        hid = None

    save = {}

    if hid is not None and hid == 1:
        try:
            ob = Interest.objects.all()
            interest_form = InterestForm(request.POST)
            if ob:
                ob = ob[0]
                interest_form = InterestForm(request.POST, instance=ob)
            if interest_form.is_valid():
                interest_form.save()
                save['form'] = ''
                save['status'] = True
            else:
                save['form'] = interest_form
                save['status'] = False

        except Interest.DoesNotExist:
            interest_form = InterestForm(request.POST)
            if interest_form.is_valid():
                interest_form.save()
                save['form'] = ''
                save['status'] = True
            else:
                save['form'] = interest_form
                save['status'] = False
    return save


def save_details(request, hid=None):
    try:
        hid = int(hid)
    except TypeError:
        hid = None
    except ValueError:
        hid = None

    save = {}

    if hid is not None and hid == 1:
        try:
            ob = ClubDetails.objects.all()
            detail_form = DetailsForm(request.POST)
            if ob:
                ob = ob[0]
                detail_form = DetailsForm(request.POST, instance=ob)
            if detail_form.is_valid():
                detail_form.save()
                save['form'] = ''
                save['status'] = True
            else:
                save['form'] = detail_form
                save['status'] = False

        except ClubDetails.DoesNotExist:
            detail_form = DetailsForm(request.POST)
            if detail_form.is_valid():
                detail_form.save()
                save['form'] = ''
                save['status'] = True
            else:
                save['form'] = detail_form
                save['status'] = False
    return save


def all_investments():
    investments = Investment.objects.all()
    if not investments:
        investments = None
    return investments


def all_contributions(monthly=0, today=None, year=None):
    if not today:
        today = date.today()

    c = Contribution.objects.all()
    if year:
        c = Contribution.objects.filter(contribution_date__year=year)
    users = User.objects.all()

    total = Decimal(0)
    credit = Decimal(0)
    outstanding = Decimal(0)

    data = []
    if users:
        for us in users:
            d = c.filter(user=us).aggregate(totals=Sum('total'))
            if not d:
                data.append({
                    'name': us,
                    'status': us.user_status,
                    'paid': 0,
                    'balance': 0
                })
            else:

                this_month = c.filter(user=us, contribution_date__month=today.month) \
                    .aggregate(Sum('total'))
                if not this_month['total__sum']:
                    this_month['total__sum'] = 0

                balance = Decimal(monthly - this_month['total__sum'])
                if balance.as_tuple().sign == 1:
                    balance = 0

                total_b = c.filter(user=us).annotate(month=TruncMonth('contribution_date')) \
                    .values('month').annotate(paid=Sum('total')).order_by('-month')

                total_balance = Decimal(0)
                for t in total_b:
                    p = t['paid']
                    y = t['month'].year
                    m = t['month'].month

                    if y == today.year and m == today.month:
                        continue

                    if total_balance.as_tuple().sign == 1:
                        total_balance += 0
                    else:
                        total_balance += Decimal(monthly - p)

                else:
                    total_balance += balance

                paid = d['totals']
                if not paid:
                    paid = 0

                expected = calculate_user_expected_amount(user=us, monthly=monthly)
                uCredit = Decimal(paid - expected)
                if uCredit.as_tuple().sign == 1:
                    uCredit = 0

                data.append({
                    'name': us,
                    'status': us.user_status,
                    'paid': paid,
                    'balance': total_balance,
                    'credit': uCredit
                })
                total += paid
                credit += uCredit
                outstanding += total_balance

    data.append({
        'total_paid': total,
        'total_credit': credit,
        'total_balance': outstanding
    })

    return data


def all_loans():
    loans = Loan.objects.all().order_by('user__first_name', 'user__last_name')
    if not loans:
        loans = None
    return loans


def cash_at_hand():
    total_expected = 0
    monthly_rate, today, start_date, months_in_operation, form = monthly_rate_today()

    contributions = all_contributions(monthly_rate, today)
    contribution_paid = contributions[-1]['total_paid']
    contribution_unpaid = contributions[-1]['total_balance']

    total_expected += (contribution_paid + contribution_unpaid)

    project_interest_and_recouped = Investment.objects.aggregate(interest=Sum('interest'),
                                                                 loss=Sum('loss'), recouped=Sum('amount_returned'))

    if project_interest_and_recouped['interest'] is None:
        project_interest_and_recouped['interest'] = 0
    if project_interest_and_recouped['loss'] is None:
        project_interest_and_recouped['loss'] = 0
    if project_interest_and_recouped['recouped'] is None:
        project_interest_and_recouped['recouped'] = 0

    investments_cash = project_interest_and_recouped['interest'] + project_interest_and_recouped['recouped']
    investments_cash -= project_interest_and_recouped['loss']

    total_expected += project_interest_and_recouped['loss']

    loans = Loan.objects.aggregate(paid=Sum('amount_paid'), unpaid=Sum('outstanding_balance'),
                                   total=Sum('loan_amount'))

    if loans['paid'] is None:
        loans['paid'] = 0
    if loans['unpaid'] is None:
        loans['unpaid'] = 0
    if loans['total'] is None:
        loans['total'] = 0

    loan_paid = loans['paid']
    loan_unpaid = loans['unpaid']

    total_expected += loans['total']

    exp = Expenses.objects.aggregate(recouped=Sum('recouped'), interest=Sum('interest'))

    if exp['recouped'] is None:
        exp['recouped'] = 0
    if exp['interest'] is None:
        exp['interest'] = 0

    expenses_paid = exp['recouped'] + exp['interest']

    actual_banked = contribution_paid + investments_cash + loan_paid + expenses_paid
    actual_unbanked = contribution_unpaid + loan_unpaid

    actual_expected = total_expected

    variance = (actual_banked + actual_unbanked) - actual_expected

    return actual_banked, actual_unbanked, actual_expected, variance


def calculate_income_statement():

    data = {
        '2015': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit':100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest':9900, 'total_cash': 690000}
        ],
        '2016': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2018': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2020': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2021': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2019': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2022': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2025': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2024': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2023': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2026': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
        '2027': [
            {'description': 'Contributions', 'debit': 2000, 'credit': 0, 'total': 5000},
            {'description': 'Expenses', 'invested': 100000, 'interest': 2000, 'recouped': 0, 'total': 67},
            {'description': 'Loans', 'debit': 0, 'credit': 100000, 'invested': 23000, 'interest': 7, 'total': 50000},
            {'description': 'Investments', 'invested': 3000, 'recouped': 6000, 'interest': 98, 'total': 7888},
            {'total_debts': 3000, 'total_credit': 2000, 'total_invested': 2000, 'total_recouped': 8700,
             'total_interest': 9900, 'total_cash': 690000}
        ],
    }

    # data = dict()
    monthly_rate, today, start_date, months_in_operation, form = monthly_rate_today()
    min_year = start_date.year
    max_year = today.year

    while min_year <= max_year:
        yearly = yearly_summary(min_year, monthly_rate)
        temp = [
            {'description': 'Contributions', 'debit': yearly['c_debit'], 'credit': yearly['c_credit'],
             'total': yearly['c_total']},
            {'description': 'Expenses', 'invested': yearly['e_invested'], 'interest': yearly['e_interest'],
             'recouped': yearly['e_recouped'], 'total': yearly['e_total']},
            {'description': 'Loans', 'debit': yearly['l_debit'], 'credit': yearly['l_credit'], 'invested': yearly['l_invested'],
             'interest': yearly['l_interest'], 'total': yearly['l_total']},
            {'description': 'Investments', 'invested': yearly['i_invested'], 'recouped': yearly['i_recouped'],
             'interest': yearly['i_interest'], 'total': yearly['i_total']},

            {'total_debts': yearly['tot_debit'], 'total_credit': yearly['tot_credit'],
             'total_invested': yearly['tot_invested'], 'total_recouped': yearly['tot_recouped'],
             'total_interest': yearly['tot_interest'], 'total_cash': yearly['tot_cash']}
        ]

        data[str(min_year)] = temp
        min_year += 1

    return OrderedDict(sorted(data.items(), key=lambda t: t[0], reverse=True))


def yearly_summary(year=None, monthly=0):
    # contributions
    c_debit = Decimal(0)
    c_credit = Decimal(0)

    # expenses
    e_invested = Decimal(0)
    e_recouped = Decimal(0)
    e_interest = Decimal(0)

    # loans
    l_debit = Decimal(0)
    l_credit = Decimal(0)
    l_invested = Decimal(0)
    l_interest = Decimal(0)

    # investments
    i_invested = Decimal(0)
    i_recouped = Decimal(0)
    i_interest = Decimal(0)

    # totals
    tot_debit = Decimal(0)
    tot_credit = Decimal(0)
    tot_invested = Decimal(0)
    tot_recouped = Decimal(0)
    tot_interest = Decimal(0)
    tot_cash = Decimal(0)

    contributions = all_contributions(monthly=monthly, year=year)
    if contributions:
        dic = contributions[-1]
        c_credit = (dic['total_paid'] + dic['total_balance'])
        c_debit = dic['total_credit']

        tot_credit += c_credit
        tot_debit += c_debit
        tot_cash += c_credit

    expense = Expenses.objects.filter(date__year=year).aggregate(invested=Sum('invested'), recouped=Sum('recouped'),
                                                                 interest=Sum('interest'))
    if expense:
        if expense['invested'] is not None:
            e_invested = expense['invested']
        if expense['recouped'] is not None:
            e_recouped = expense['recouped']
        if expense['interest'] is not None:
            e_interest = expense['interest']
        tot_invested += e_invested
        tot_interest += e_interest
        tot_recouped += e_recouped
        tot_cash += (e_recouped + e_interest)

    investments = Investment.objects.filter(create_date__year=year).aggregate(
        invested=Sum('total_capital_invested'), recouped=Sum('amount_returned'), interest=Sum('interest'))
    if investments:
        if investments['invested'] is not None:
            i_invested = investments['invested']
        if investments['recouped'] is not None:
            i_recouped = investments['recouped']
        if investments['interest'] is not None:
            i_interest = investments['interest']
        tot_invested += i_invested
        tot_interest += i_interest
        tot_recouped += i_recouped
        tot_cash += (i_recouped + i_interest)

    loan = Loan.objects.filter(loan_date__year=year).aggregate(
        invested=Sum('loan_amount'), credit=Sum('amount_paid'), debts=Sum('outstanding_balance'),
        interest=Sum('loan_interest'))
    if loan:
        if loan['interest'] is not None:
            l_interest = loan['interest']
        if loan['invested'] is not None:
            l_invested = loan['invested']
        if loan['debts'] is not None:
            l_debit = loan['debts']
        if loan['credit'] is not None:
            l_credit = loan['credit']
        tot_invested += l_invested
        tot_interest += l_interest
        tot_debit += l_debit
        tot_credit += l_credit
        tot_cash += l_credit

    data = {
        'c_debit': c_debit, 'c_credit': c_credit, 'c_total': c_credit,
        'e_invested': e_invested, 'e_interest': e_interest, 'e_recouped': e_recouped,
        'e_total': (e_recouped + e_interest),
        'l_debit': l_debit, 'l_credit': l_credit, 'l_invested': l_invested, 'l_interest': l_interest,
        'l_total': l_credit,
        'i_invested': i_invested, 'i_recouped': i_recouped, 'i_interest': i_interest,
        'i_total': (i_recouped + i_interest),
        'tot_debit': tot_debit, 'tot_credit': tot_credit, 'tot_invested': tot_invested,
        'tot_recouped': tot_recouped, 'tot_interest': tot_interest, 'tot_cash': tot_cash,
    }
    return data


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    s_url = settings.STATIC_URL
    s_root = settings.STATIC_ROOT
    m_url = settings.MEDIA_URL
    m_root = settings.MEDIA_ROOT

    # convert URIs to absolute system paths
    if uri.startswith(m_url):
        path = os.path.join(m_root, uri.replace(m_url, ""))
    elif uri.startswith(s_url):
        path = os.path.join(s_root, uri.replace(s_url, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (s_url, m_url)
        )
    return path


class PrintFunction(View):

    global my_css

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

                # using xhtml2pdf and not weasyprint to generate admin summary PDF file
                name = '{0}.pdf'.format(generate_report_filename())
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="{0}.pdf"'.format(name)

                pisaStatus = pisa.CreatePDF(out_put, dest=response, link_callback=link_callback,
                                            default_css=my_css)
                # if error then show some funy view
                if pisaStatus.err:
                    return HttpResponse('We had some errors <pre>' + out_put + '</pre>')
                return response

            except Exception as ex:
                raise Resolver404('Error Occurered while creating Admin PDF Template: ' + str(ex.message))

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

                # using weasyprint to print the user profile PDF page
                try:
                    name = '{0}.pdf'.format(generate_report_filename())
                    HTML(string=out_put, base_url=request.build_absolute_uri()).write_pdf(
                        os.path.join(REPORT_ROOT, name))

                    fs = FileSystemStorage(REPORT_ROOT)

                    with fs.open(name) as pdf:
                        response = HttpResponse(pdf, content_type='application/pdf')
                        response['Content-Disposition'] = 'inline; filename={0}.pdf'.format(name)
                        return response

                except Exception as e:
                    raise Resolver404('An Error Occurred... While processing the file' + str(e.message))

            except TemplateDoesNotExist:
                raise Resolver404('User Template Not Found')

        else:
            raise Resolver404('URL Not Understood')


class ExcelFunction(View):

    file_name = None
    columns = []
    query_sets = None
    file_type = 'xlsx'
    date_today = str(datetime.today())

    def get(self, request, what=None):

        if not request.user.is_authenticated():
            return redirect('login_user')

        if not what:
            raise Resolver404('Not Found')

        if what == 'users':
            if not request.user.has_perms(['can_view_user']):
                raise PermissionDenied('permission denied')
            self.query_sets = User.objects.all()
            self.columns = ['account_id', 'first_name', 'last_name', 'email',
                            'contact', 'address', 'date_joined', 'username', 'user_status']
            self.file_name = 'members-list-' + self.date_today

        elif what == 'contributions':
            if not request.user.has_perms(['can_view_contributions']):
                raise PermissionDenied('permission denied')
            self.query_sets = Contribution.objects.all()
            self.columns = ['user_id', 'contribution_date', 'deposit', 'penalty', 'total']
            self.file_name = 'contributions-list-' + self.date_today

        elif what == 'investments':
            if not request.user.has_perms(['can_view_investments']):
                raise PermissionDenied('permission denied')
            self.file_name = 'investments-list-' + self.date_today
            return excel.make_response_from_a_table(Investment, self.file_type, file_name=self.file_name)

        elif what == 'loans':
            if not request.user.has_perms(['can_view_loans']):
                raise PermissionDenied('permission denied')
            self.query_sets = Loan.objects.all()
            self.columns = ['user_id', 'loan_date', 'loan_duration', 'loan_amount', 'amount_paid',
                            'sur_charge', 'sub_total', 'loan_interest', 'total_amount',
                            'outstanding_balance', 'loan_status']
            self.file_name = 'Loans-list-' + self.date_today

        elif what == 'user_contributions':
            self.query_sets = Contribution.objects.filter(user=request.user)
            self.columns = ['user_id', 'contribution_date', 'deposit', 'penalty', 'total']
            self.file_name = 'my_contributions-' + self.date_today

        else:
            raise Resolver404('URL Not Understood')

        if not self.query_sets or not self.columns or not self.file_name:
            raise Resolver404('Could Not export data')

        try:
            return excel.make_response_from_query_sets(self.query_sets, self.columns,
                                                       self.file_type, file_name=self.file_name)
        except Exception as e:
            raise e
