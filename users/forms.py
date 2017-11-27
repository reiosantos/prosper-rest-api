
from __future__ import unicode_literals

from crispy_forms.bootstrap import FormActions, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Button
from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm, TextInput, RadioSelect, FileInput
from django.utils.translation import ugettext_lazy

from home.support.support_functions import get_corrected_permissions
from users.models import User


class UserForm(ModelForm):
    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal user_form'
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    helper.form_action = 'add_user'
    helper.form_method = 'post'
    helper.form_show_errors = True

    helper.layout = Layout(
        Field('account_id', css_class='input-sm', ),
        PrependedText('first_name', 'A', css_class='input-sm', ),
        PrependedText('last_name', 'Z', css_class='input-sm'),
        PrependedText('address', '<i class="fa fa-map"></i>', css_class='input-sm'),
        PrependedText('email', '<i class="fa fa-envelope"></i>', css_class='input-sm'),
        PrependedText('contact', '<i class="fa fa-phone"></i>', css_class='input-sm'),
        Field('photo', css_class='input-sm user_photo'),
        PrependedText('username', '<i class="fa fa-user"></i>', css_class='input-sm'),
        PrependedText('password', '<i class="fa fa-lock"></i>', css_class='input-sm'),

        FormActions(
            Submit('submit', 'Send Request', css_class="btn-primary"),
            Button('cancel', 'Clear'),
        ),
    )

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['account_id', 'first_name', 'last_name',
                  'email', 'contact', 'username', 'password',
                  'address', 'photo', ]
        widgets = {
            'account_id': TextInput(attrs={'readonly': 'readonly'}),
            'password': TextInput(attrs={'value': '12345abcde'}),
            'photo': FileInput(attrs={'accept': 'image/*'})
        }


class AdminUserForm(ModelForm):

    user_permissions = forms.ModelMultipleChoiceField(
        get_corrected_permissions(),
        help_text=ugettext_lazy('Specific permissions for this user.'),
    )
    # Uni-form
    helper = FormHelper()
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    helper.form_tag = False
    helper.form_show_errors = True

    helper.layout = Layout(
        Field('account_id', css_class='input-sm',),
        PrependedText('first_name', 'A', css_class='input-sm',),
        PrependedText('last_name', 'Z', css_class='input-sm'),
        PrependedText('address', '<i class="fa fa-map"></i>',  css_class='input-sm'),
        PrependedText('email', '<i class="fa fa-envelope"></i>', css_class='input-sm'),
        PrependedText('contact', '<i class="fa fa-phone"></i>', css_class='input-sm'),
        Field('photo', css_class='input-sm user_photo'),
        PrependedText('username', '<i class="fa fa-user"></i>', css_class='input-sm'),
        PrependedText('password', '<i class="fa fa-lock"></i>', css_class='input-sm'),
        Field('user_type', css_class='input-sm'),
        Field('is_staff', css_class='input-sm'),
        Field('is_superuser', style="background: #FAFAFA; padding: 10px;"),
        Field('user_status'),
        'user_permissions',
    )

    def save(self, commit=True):
        user = super(AdminUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            for permission in self.cleaned_data['user_permissions']:
                user.user_permissions.add(permission)
            if not user.has_perm('can_not_do_much'):
                content_type = ContentType.objects.get_for_model(User)
                perm = Permission.objects.get(codename='can_not_do_much', content_type=content_type)
                user.user_permissions.add(perm)
        return user

    class Meta:
        model = User
        fields = ['account_id', 'first_name', 'last_name',
                  'email', 'contact', 'is_staff', 'username', 'password',
                  'address', 'photo', 'user_type', 'user_permissions',
                  'is_superuser', 'user_status']
        widgets = {
            'user_type': RadioSelect,
            'user_status': forms.Select,
            'account_id': TextInput(attrs={'readonly': 'readonly'}),
            'password': TextInput(attrs={'value': '12345abcde'}),
            'photo': FileInput(attrs={'accept': 'image/*'}),
            'user_permissions': forms.CheckboxSelectMultiple()
        }
