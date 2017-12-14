
from datetime import date
from dateutil import relativedelta

from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from finance.forms import InterestForm
from finance.models import Interest, Investment, Contribution, Loan, LoanPayment
from home.forms import DetailsForm
from home.models import ClubDetails, Expenses
from users.models import User


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
                if num[months_passed - 1]['month'].year == timezone.now().year and num[months_passed - 1]['month'].month < \
                        timezone.now().month:
                    months_passed += 1
            else:
                months_passed += 1
        elif time_passed.hours or time_passed.minutes and not time_passed.days:
            months_passed += 1
            
    return months_passed,  time_passed


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
        time_since = str(time_passed.hours) + ' hour(s), and ' + str(time_passed.minutes) +\
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


def all_contributions(monthly=0, today=None):
    if not today:
        today = date.today()

    c = Contribution.objects.all()
    users = User.objects.all()

    total = Decimal(0)
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

                this_month = Contribution.objects.filter(user=us, contribution_date__month=today.month)\
                    .aggregate(Sum('total'))
                if not this_month['total__sum']:
                    this_month['total__sum'] = 0

                balance = Decimal(monthly - this_month['total__sum'])
                if balance.as_tuple().sign == 1:
                    balance = 0

                total_b = Contribution.objects.filter(user=us).annotate(month=TruncMonth('contribution_date')) \
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
                data.append({
                    'name': us,
                    'status': us.user_status,
                    'paid': paid,
                    'balance': total_balance
                })
                total += paid
                outstanding += total_balance

    data.append({
        'total_paid': total,
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

    loans = Loan.objects.aggregate(profit=Sum('profit_earned'), paid=Sum('amount_paid'),
                                   unpaid=Sum('outstanding_balance'), total=Sum('loan_amount'))

    if loans['profit'] is None:
        loans['profit'] = 0
    if loans['paid'] is None:
        loans['paid'] = 0
    if loans['unpaid'] is None:
        loans['unpaid'] = 0
    if loans['total'] is None:
        loans['total'] = 0

    loan_paid = loans['paid'] + loans['profit']
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
            {'description': 'contributions', 'debit':'230000', 'credit':'34000000', 'total':'23000000' },
            {'description': 'expenses', 'debit':'230000', 'credit':'34000000', 'total':'23000000' },
            {'description': 'recouped', 'debit':'230000', 'credit':'34000000', 'total':'23000000' },
            {'description': 'Bank interest', 'debit':'230000', 'credit':'34000000', 'total':'23000000' },
            {'total_debts': '12000000', 'total_credit':'230000', 'total_cash':'23000000' },
        ],
        '2016': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2017': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2018': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2019': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2020': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2021': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2022': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2023': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2024': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2025': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2026': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2027': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
        '2028': [
            {'description': 'contributions', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'expenses', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'recouped', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'description': 'Bank interest', 'debit': '230000', 'credit': '34000000', 'total': '23000000'},
            {'total_debts': '12000000', 'total_credit': '230000', 'total_cash': '23000000'},
        ],
    }

    """
    contributions = Contribution.objects.annotate(year=TruncYear('contribution_date')) \
                    .values('year').annotate(paid=Sum('total')).order_by('-year')
    """

    return data
