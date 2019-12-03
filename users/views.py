from datetime import date
from dateutil import relativedelta

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.db.models.query_utils import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from home.support.support_functions import get_user_contributions, get_user_investments, get_user_loans
from home.support.validators import get_corrected_permissions
from users.forms import UserForm, AdminUserForm
from users.models import User


@require_http_methods(["GET", "POST"])
def login_user(request):

    if request.user.is_authenticated:
        return redirect('home_page')

    next_page = request.GET.get('next', 'home_page')

    if request.method == 'POST':
        next_page = request.POST.get('next', 'home_page')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.user_status == 'pending':
                error = "Your account has not yet been approved. Please wait for an email confirmation and try again"
                return render(request, 'registration/login.html', {'error': error})
            if not user.user_status == 'active':
                error = "You do not have an account with us. Kindly" \
                        " send in an account request and we shall activate your account"
                return render(request, 'registration/login.html', {'error': error})

            login(request, user)
            if not next_page:
                next_page = 'home_page'
            return redirect(next_page)
        else:
            error = " Invalid Credentials. Your username and password didn't match. Try Again"
            return render(request, 'registration/login.html', {'error': error})
    else:
        return render(request, 'registration/login.html', {'next': next_page})


@require_GET
def logout_user(request):
    logout(request)
    return redirect("login_user")


@require_http_methods(["GET", "POST"])
def add_user(request):
    form = UserForm()
    message = ''

    if request.POST:
        form = UserForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            form = UserForm()
            message = 'Your request has been sent.. Please wait for a confirmation email that confirms your membership'

    return render(request, 'users/user_form.html', {
        'title': "New user request",
        'no_search': True,
        'form': form,
        'message': message,
    })


@require_http_methods(["GET", "POST"])
def manage_users(request):

    if not request.user.has_perms(['can_view_user']):
        raise PermissionDenied('permission denied')

    message = ''
    admin_form = AdminUserForm()

    if request.is_ajax():
        table = request.POST.get('table', False)
        search = request.POST.get('search', False)
        if table and table == 'users':
            accounts = User.objects.filter(~Q(user_status='pending'),
                                           Q(account_id__icontains=search) |
                                           Q(first_name__icontains=search) |
                                           Q(last_name__icontains=search))
            data = {}
            if accounts:
                for account in accounts:
                    d = {
                        'account_id': account.account_id,
                        'first_name': account.first_name,
                        'last_name': account.last_name,
                        'address': account.address,
                        'email': account.email,
                        'contact': account.contact,
                        'username': account.username,
                        'user_type': account.user_type,
                        'is_superuser': account.is_superuser,
                        'user_status': account.user_status,
                        'date_joined': date.strftime(account.date_joined, "%b. %d, %Y, %I:%M %P"),
                    }
                    data[str(account.date_joined)] = d
                return JsonResponse(data)
            else:
                return JsonResponse(data)

    if request.POST:
        admin_form = AdminUserForm(request.POST, request.FILES)
        try:
            my_user = User.objects.get(account_id=request.POST['account_id'])
        except User.DoesNotExist:
            my_user = ''

        if my_user:
            perms = get_corrected_permissions(my_user)
            if not request.POST.get('is_super_user', False):
                for perm in perms:
                    my_user.user_permissions.remove(perm)

            admin_form = AdminUserForm(request.POST, request.FILES, instance=my_user)
            current_password = my_user.password

            if admin_form.is_valid():
                updataed_model = admin_form.save()
                updataed_model.password = current_password
                updataed_model.save()

                admin_form = AdminUserForm()
                message = 'user Information has been updated'

        elif admin_form.is_valid():
            admin_form.save()
            admin_form = AdminUserForm()
            message = 'New user has been registered and is active'

    old_users_list = User.objects.filter(~Q(user_status='pending'))
    new_users_list = User.objects.filter(Q(user_status='pending'))

    return render(request, 'users/user_form_admin.html', {
        'title': "User Manager",
        'search_table': 'users',
        'to_print': 'Members List',
        'what_to_print': 'users',
        'form': admin_form,
        'new_users': new_users_list,
        'old_users': old_users_list,
        'message': message,
    })


@require_POST
@ensure_csrf_cookie
def ajax(request):
    if not request.is_ajax():
        return False
    ids = request.POST.get('id', False)
    account = User.objects.get(account_id=ids)
    if not account:
        return False

    if account.photo:
        photo = account.photo.name
    else:
        photo = False

    perms = get_corrected_permissions(account)
    perm_dict = {}
    for permission in perms:
        perm_dict[permission.id] = permission.name

    data = {
        'account_id': account.account_id,
        'first_name': account.first_name,
        'last_name': account.last_name,
        'address': account.address,
        'email': account.email,
        'contact': account.contact,
        'is_staff': account.is_staff,
        'photo': photo,
        'username': account.username,
        'password': '***************',
        'user_type': account.user_type,
        'is_superuser': account.is_superuser,
        'user_status': account.user_status,
        'user_permissions': perm_dict,
    }
    return JsonResponse(data)


def profile(request):

    if not request.user.is_authenticated():
        return redirect('login_user')

    today = date.today()

    contribution = get_user_contributions(request.user, today)
    investment = get_user_investments(request)
    loan = get_user_loans(request)

    return render(request, 'users/profile.html',
                  {
                      'title': "My Profile",
                      'no_search': True,
                      'contributions': contribution['contributions'],
                      'summary': contribution['summary'],
                      'i_manage': investment['i_manage'],
                      'a_member': investment['a_member'],
                      'others': investment['other'],
                      'on_loan': loan['on_loan'],
                      'on_pay': loan['on_pay'],
                      'credit': loan['credit'],
                  })


def profile_graph(request):

    if not request.user.is_authenticated():
        return redirect('login_user')

    months_passed = relativedelta.relativedelta(timezone.now(), request.user.date_joined)
    if not months_passed.years and not months_passed.months:
        time_since = str(months_passed.days) + ' day(s), since you joined the group!!'
    elif not months_passed.years:
        time_since = str(months_passed.months) + ' month(s) and ' + str(months_passed.days) + \
                     ' day(s), since you joined the group!!'
    elif months_passed.years:
        time_since = str(months_passed.years) + ' year(s), ' + str(months_passed.months) + ' month(s) and ' + \
                     str(months_passed.days) + ' day(s), since you joined the group!!'
    else:
        time_since = ''

    return render(request, 'users/profile_graph.html',
                  {
                      'title': "My Profile",
                      'no_search': True,
                      'time_spent': time_since,
                  })
