
from datetime import date

from django.core.exceptions import PermissionDenied
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from django.forms.models import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from finance.forms import ContributionForm, ExcelUploadForm, InvestmentForm, InvestmentFinancialStatementForm, \
    InterestForm, LoanForm, LoanPaymentForm
from finance.models import Contribution, Investment, InvestmentFinancialStatement, Interest, Loan, LoanPayment
from home.support.support_functions import save_interest
from home.support.validators import RequiredFormset


def investments(request):
    if not request.user.has_perms(['can_add_investment']):
        raise PermissionDenied('permission denied')

    message = ''
    error = ''
    default_rate = 0
    today = date.today()
    initials = {
        'project_manager': request.user,
        'project_status': 'in_progress'
    }
    admin_investment_form = InvestmentForm(initial=initials)

    if request.is_ajax():
        return investment_ajax_search(request)

    if request.POST:
        admin_investment_form = InvestmentForm(request.POST)

        if admin_investment_form.is_valid():
            admin_investment_form.save()
            message = 'Investment has been logged'
            admin_investment_form = InvestmentForm(initial=initials)
        else:
            error = 'Investment form has invalid data.. '

    old_list = Investment.objects.all()
    new_list = Investment.objects.filter(Q(create_date__year=today.year) & Q(create_date__month=today.month))[:5]

    return render(request, 'finance/investments_admin.html', {
        'title': "Investments",
        'search_table': "investments",
        'table_url': reverse('investments_update'),
        'num': new_list.count(),
        'default_rate': default_rate,
        'investment_form': admin_investment_form,
        'new_investments': new_list,
        'all_investments': old_list,
        'message': message,
        'error': error,
    })


def investments_update(request, ids=False):

    if not request.user.has_perms(['can_modify_investment']):
        raise PermissionDenied('permission denied')

    message = ''
    error = ''
    default_rate = 0
    no_of_forms = 1
    has_investments = False
    today = date.today()
    initials = {
        'project_manager': request.user,
        'project_status': 'in_progress',
        'project_rating': default_rate
    }

    if request.is_ajax():
        return investment_ajax_search(request)

    financial_formset = modelformset_factory(InvestmentFinancialStatement,
                                             InvestmentFinancialStatementForm,
                                             extra=no_of_forms, can_order=True,
                                             can_delete=True, formset=RequiredFormset)
    admin_investment_form = InvestmentForm(initial=initials, update=True)
    admin_financial_formset = financial_formset(queryset=InvestmentFinancialStatement.objects.none())

    try:
        ids = int(ids)
    except TypeError:
        ids = None
    except ValueError:
        ids = None

    if not ids and not request.POST:
        return redirect('investments')

    if ids and not request.POST:
        try:
            investment_instance = Investment.objects.get(id=ids)

            investment_financial_instance = InvestmentFinancialStatement.objects.filter(investment_id__exact=ids)
            if investment_instance:
                admin_investment_form = InvestmentForm(instance=investment_instance, update=True)
                default_rate = investment_instance.project_rating
                admin_investment_form.add_hidden(investment_instance.id)

            if investment_instance and investment_financial_instance:
                admin_financial_formset = financial_formset(queryset=investment_financial_instance)
                admin_financial_formset.forms[-1].fields['investment'].initial = investment_instance

            else:
                if investment_instance:
                    for form in admin_financial_formset:
                        form.fields['investment'].initial = investment_instance

        except Investment.DoesNotExist:
            return redirect('investments')
            # error = 'Investment Object requested does not exist'

    old_list = Investment.objects.all()
    if old_list:
        has_investments = True

    if request.POST:
        ac_id = request.POST.get('hidden_investment', False)
        if not ac_id:
            error = 'Investment %s does not exist' % ac_id
        else:
            admin_investment_form.add_hidden(ac_id)
            invest = Investment.objects.get(id=ac_id)
            if invest:
                invest.project_team.clear()

                admin_investment_form = InvestmentForm(request.POST, instance=invest, update=True)

                if admin_investment_form.is_valid():

                    investment = admin_investment_form.save(commit=False)
                    for choice in admin_investment_form.cleaned_data['project_team']:
                        investment.project_team.add(choice)

                    admin_financial_formset = financial_formset(request.POST, request.FILES)
                    if admin_financial_formset.is_valid():

                        InvestmentFinancialStatement.objects.filter(investment_id__exact=investment.id).delete()
                        for form in admin_financial_formset.forms:
                            if form.is_valid():
                                if form.has_changed():
                                    stat = form.save(commit=False)
                                    stat.investment = investment
                                    stat.save()
                        else:
                            investment.save()
                            message = 'Investment update has commited'
                            admin_investment_form = None
                            # admin_investment_form = InvestmentForm(initial=initials, update=True)
                            admin_financial_formset = None
                            # admin_financial_formset =
                            # financial_formset(queryset=InvestmentFinancialStatement.objects.none())
                    else:
                        error = 'financial form has invalid data...'
                else:
                    error = 'Investment form has invalid data.. '

    old_list = Investment.objects.all()
    new_list = Investment.objects.filter(Q(create_date__year=today.year, create_date__month=today.month))[:5]

    return render(request, 'finance/investments_admin_update.html', {
        'title': "Investments",
        'search_table': "investments",
        'table_url': reverse('investments_update'),
        'num': new_list.count(),
        'has_investments': has_investments,
        'investment_form': admin_investment_form,
        'financial_forms': admin_financial_formset,
        'new_investments': new_list,
        'all_investments': old_list,
        'default_rate': default_rate,
        'message': message,
        'error': error,
    })


def investment_ajax_search(request):
    if request.is_ajax():
        table = request.POST.get('table', False)
        search = request.POST.get('search', False)

        if table and table == 'investments':
            ajax_investments = Investment.objects.filter(Q(project_name__icontains=search) |
                                                         Q(project_manager__first_name__icontains=search) |
                                                         Q(project_manager__last_name__icontains=search))
            data = {}
            if ajax_investments:
                for investment in ajax_investments:
                    d = {
                        'manager': investment.project_manager.first_name + " " + investment.project_manager.last_name,
                        'project_name': investment.project_name,
                        'project_id': investment.id,
                        'start_date': date.strftime(investment.start_date, "%b. %d, %Y, %I:%M %P"),
                        'age': investment.project_age,
                        'status': investment.project_status,
                        'rating': investment.project_rating,
                        'capital': investment.total_capital_invested,
                        'interest': investment.interest,
                        'loss': investment.loss,
                    }
                    data[str(investment.start_date)] = d
                return JsonResponse(data)
            else:
                return JsonResponse(data)


def loans_ajax_search(request):
    if request.is_ajax():
        table = request.POST.get('table', False)
        search = request.POST.get('search', False)

        if table and table == 'loans':
            ajax_loans = Loan.objects.filter(Q(loan_status__icontains=search) |
                                             Q(user__first_name__icontains=search) |
                                             Q(user__last_name__icontains=search))
            data = {}
            if ajax_loans:
                for loan in ajax_loans:
                    d = {
                        'user': loan.user.first_name + " " + loan.user.last_name,
                        'loan_duration': loan.loan_duration,
                        'id': loan.pk,
                        'loan_date': date.strftime(loan.loan_date, "%b. %d, %Y, %I:%M %P"),
                        'amount': loan.loan_amount,
                        'interest': loan.loan_interest,
                        'total': loan.total_amount,
                        'paid': loan.amount_paid,
                        'balance': loan.outstanding_balance,
                        'profit': loan.profit_earned,
                        'status': loan.loan_status,
                    }
                    data[str(loan.loan_date)] = d
                return JsonResponse(data)
            else:
                return JsonResponse(data)


def contributions(request):
    message = ''
    error = ''
    admin_form = ContributionForm()
    excel_form = ExcelUploadForm()

    today = date.today()

    if request.is_ajax():
        table = request.POST.get('table', False)
        search = request.POST.get('search', False)
        if table and table == 'contributions':
            accounts = Contribution.objects.filter(
                Q(user__account_id__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)).order_by('-contribution_date')
            data = {}
            if accounts:
                for account in accounts:
                    if account.deposit_slip:
                        slip = account.deposit_slip.name
                    else:
                        slip = ''
                    d = {
                        'id': account.pk,
                        'account_id': account.user_id,
                        'first_name': account.user.first_name,
                        'last_name': account.user.last_name,
                        'deposit': account.deposit,
                        'penalty': account.penalty,
                        'total': account.total,
                        'contribution_date': date.strftime(account.contribution_date, "%b. %d, %Y, %I:%M %P"),
                        'deposit_slip': slip,
                    }
                    data[str(account.contribution_date)] = d
                return JsonResponse(data)
            else:
                return JsonResponse(data)
        else:
            ids = request.POST.get('id', False)
            try:
                ids = int(ids)
            except TypeError:
                ids = None
            except ValueError:
                ids = None

            if id:
                try:
                    con = Contribution.objects.get(pk=ids)
                    if con:
                        if con.deposit_slip:
                            slip = con.deposit_slip.name
                        else:
                            slip = ''
                        d = {
                            'id': con.pk,
                            'account_id': con.user_id,
                            'deposit': con.deposit,
                            'penalty': con.penalty,
                            'total': con.total,
                            'contribution_date': date.strftime(con.contribution_date, "%Y-%m-%d %H:%M:%S"),
                            'deposit_slip': slip,
                        }
                        return JsonResponse(d)
                    else:
                        return False
                except Contribution.DoesNotExist:
                    return False

    if request.POST:

        ids = request.POST.get('hidden_contribution', None)
        try:
            ids = int(ids)
        except TypeError:
            ids = None
        except ValueError:
            ids = None

        if request.POST.get('identity', False):
            excel_form = ExcelUploadForm(request.POST, request.FILES)
            if excel_form.is_valid():
                # to handle uploads of excel

                message = 'Contributions have been uploaded'
        elif ids is not None and ids is not False:
            if ids is not None:
                try:
                    con = Contribution.objects.get(pk=ids)
                    if con:
                        admin_form = ContributionForm(request.POST, request.FILES, instance=con)
                        if admin_form.is_valid():
                            admin_form.save()
                            message = 'Contribution has been Updated'
                            admin_form = ContributionForm()
                    else:
                        error = 'failed to commit update.... check the form your submitting'
                except Contribution.DoesNotExist:
                    error = 'The selected contribution for update does not exist...'
            else:
                error = 'This request session expired, please reload the page'
        else:
            admin_form = ContributionForm(request.POST, request.FILES)

            if admin_form.is_valid():
                admin_form.save()
                admin_form = ContributionForm()
                message = 'Contribution has been saved'
            else:
                error = 'failed to add contribution.... check the form your submitting'

    old_list = Contribution.objects.all()
    my_list = Contribution.objects.filter(
        Q(user__account_id__exact=request.user.account_id)).order_by('-contribution_date')[:10]
    my_total = Contribution.objects.filter(
        Q(user__account_id__exact=request.user.account_id)).aggregate(total_sum=Sum('total'))
    new_list = Contribution.objects.filter(
        Q(contribution_date__year=today.year, contribution_date__month=today.month))[:5]

    if request.user.has_perms(['can_view_contribution']):
        template = 'finance/contributions_admin.html'
    else:
        template = 'finance/contributions.html'

    admin_form.add_hidden(False)

    return render(request, template, {
        'title': "Contributions",
        'search_table': "contributions",
        # 'table_url': reverse('contributions_update'),
        'form': admin_form,
        'num': new_list.count(),
        'my_num': 10,
        'new_contributions': new_list,
        'excel_form': excel_form,
        'contributions': old_list,
        'my_contributions': my_list,
        'my_total': my_total,
        'message': message,
        'error': error,
    })


def loans(request):

    if not request.user.has_perms(['can_add_loan']):
        raise PermissionDenied('permission denied')

    message = ''
    error = ''
    admin_loan_form = LoanForm()

    try:
        ob = Interest.objects.all()
        interest_form = InterestForm()
        if ob:
            ob = ob[0]
            interest_form = InterestForm(instance=ob)
    except Interest.DoesNotExist:
        interest_form = InterestForm()

    if request.is_ajax():
        return loans_ajax_search(request)

    if request.POST:

        hid = request.POST.get('hidden_interest', False)
        if hid and hid is not False:
            save = save_interest(request, hid)
            if save['status']:
                ob = Interest.objects.all()
                if ob:
                    ob = ob[0]
                    interest_form = InterestForm(instance=ob)
                else:
                    interest_form = InterestForm()
                message = 'Interest rate updated'
            else:
                interest_form = save['form']
                error = 'Failed to complete update'

        else:

            admin_loan_form = LoanForm(request.POST)
            if admin_loan_form.is_valid():

                ln = admin_loan_form.save(commit=False)
                loan = Loan.objects.filter(user=ln.user, loan_status='running')

                if loan and loan.count() > 0:
                    error = ln.user.__str__() + ' cannot get another loan before paying off the current loan'
                else:
                    ln.save()
                    message = 'Laon has been saved'
                    admin_loan_form = LoanForm()
            else:
                error = 'Loan form has invalid data.. '

    old_list = Loan.objects.all()
    new_list = Loan.objects.filter(Q(loan_status='running'))

    return render(request, 'finance/loans.html', {
        'title': "Loans",
        'search_table': "loans",
        'table_url': reverse('loans_update'),
        'num_on_loan': new_list.count(),
        'interest_form': interest_form,
        'loan_form': admin_loan_form,
        'new_loans': new_list,
        'all_loans': old_list,
        'message': message,
        'error': error,
    })


def loans_update(request, ids=False):

    if request.is_ajax():
        return loans_ajax_search(request)

    if not request.user.has_perms(['can_modify_loan']):
        raise PermissionDenied('permission denied')

    message = ''
    error = ''
    no_of_forms = 1

    try:
        ids = int(ids)
    except TypeError:
        ids = None
    except ValueError:
        ids = None

    admin_loan_form = LoanForm()
    payment_formset = modelformset_factory(LoanPayment,
                                           LoanPaymentForm,
                                           extra=no_of_forms, can_order=False,
                                           can_delete=False, formset=RequiredFormset)
    admin_payment_formset = payment_formset(queryset=LoanPayment.objects.none())

    if not ids and not request.POST:
        return redirect('loans')

    if ids and not request.POST:
        try:
            loan_instance = Loan.objects.get(id=ids)

            loan_payment_instance = LoanPayment.objects.filter(loan_id__exact=ids)
            if loan_instance:
                admin_loan_form = LoanForm(instance=loan_instance)
                admin_loan_form.add_hidden(loan_instance.id)

            if loan_instance and loan_payment_instance:
                admin_payment_formset = payment_formset(queryset=loan_payment_instance)
                admin_payment_formset.forms[-1].fields['loan'].initial = loan_instance

            else:
                if loan_instance:
                    for form in admin_payment_formset:
                        form.fields['loan'].initial = loan_instance

        except Investment.DoesNotExist:
            return redirect('loans')

    try:
        ob = Interest.objects.all()
        interest_form = InterestForm()
        if ob:
            ob = ob[0]
            interest_form = InterestForm(instance=ob)
    except Interest.DoesNotExist:
        interest_form = InterestForm()

    if request.POST:

        hid = request.POST.get('hidden_interest', False)
        if hid and hid is not False:
            save = save_interest(request, hid)
            if save['status']:
                ob = Interest.objects.all()
                if ob:
                    ob = ob[0]
                    interest_form = InterestForm(instance=ob)
                else:
                    interest_form = InterestForm()
                message = 'Interest rate updated'
            else:
                interest_form = save['form']
                error = 'Failed to complete update'
        else:
            loan_id = request.POST.get('hidden_loan', False)
            if not loan_id:
                error = 'Loan %s does not exist' % loan_id
            else:
                admin_loan_form.add_hidden(loan_id)
                loan = Loan.objects.get(id=loan_id)
                if loan:
                    admin_loan_form = LoanForm(request.POST, instance=loan)
                    if admin_loan_form.is_valid():
                        loan = admin_loan_form.save(commit=False)

                        admin_payment_formset = payment_formset(request.POST, request.FILES)
                        if admin_payment_formset.is_valid():

                            LoanPayment.objects.filter(loan_id__exact=loan.id).delete()
                            total_paid = 0
                            for form in admin_payment_formset.forms:
                                if form.is_valid():
                                    stat = form.save(commit=False)
                                    if stat.paid_amount == 0:
                                        continue
                                    stat.loan = loan
                                    stat.save()
                                    total_paid += stat.paid_amount
                            else:
                                try:
                                    ob = Interest.objects.all()
                                    rate = 15
                                    if ob:
                                        ob = ob[0]
                                        rate = ob.interest
                                except Interest.DoesNotExist:
                                    rate = 15

                                if loan.calculate_amounts(paid=total_paid, rate=rate):
                                    loan.save()
                                    message = 'Loan update has been successful'
                                    admin_loan_form = None
                                    admin_payment_formset = None
                                else:
                                    error = 'failed to save changes, due to either invalid rates or paid amount'
                        else:
                            error = 'Payment form has invalid data...'
                    else:
                        error = 'Loan form has invalid data.. '

    old_list = Loan.objects.all()
    new_list = Loan.objects.filter(Q(loan_status='running'))

    return render(request, 'finance/loans_update.html', {
        'title': "Loans",
        'search_table': "loans",
        'table_url': reverse('loans_update'),
        'num_on_loan': new_list.count(),
        'interest_form': interest_form,
        'loan_form': admin_loan_form,
        'payment_forms': admin_payment_formset,
        'new_loans': new_list,
        'all_loans': old_list,
        'message': message,
        'error': error,
    })


def statements(request):
    return render(request, 'base_template.html', {'question': "whu  me"})
