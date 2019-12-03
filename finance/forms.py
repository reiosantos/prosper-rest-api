
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from crispy_forms.bootstrap import PrependedText, TabHolder, Tab, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Hidden, Fieldset, Div, HTML
from django.forms import ModelForm, TextInput, FileInput, forms, DateTimeInput, Select, NumberInput

from config.settings import FILE_UPLOAD_MAX_MEMORY_SIZE
from finance.models import Investment, InvestmentFinancialStatement, Contribution, Interest, Loan, LoanPayment
from home.support.validators import FileValidator


class ContributionForm(ModelForm):

    helper = FormHelper()
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    helper.form_tag = False
    helper.form_show_errors = True

    helper.layout = Layout(
        Field('user', css_class='input-sm'),
        PrependedText('contribution_date', '<i class="fa fa-calendar"></i>', css_class='input-sm date-input'),
        PrependedText('deposit', 'UGX', css_class='input-sm'),
        PrependedText('penalty', 'UGX', css_class='input-sm'),
        PrependedText('total', 'UGX', css_class='input-sm'),
        Field('deposit_slip', css_class='input-sm'),
    )

    def add_hidden(self, ids):
        hidden = Hidden(name='hidden_contribution', value=ids, css_class='input-sm')
        self.helper.add_input(hidden)

    class Meta:
        model = Contribution
        fields = ['user',
                  'contribution_date', 'deposit', 'penalty', 'total', 'deposit_slip']
        widgets = {
            'total': TextInput(attrs={'readonly': 'readonly'}),
            'deposit_slip': FileInput(attrs={'accept': 'application/pdf'})
        }


class ExcelUploadForm(forms.Form):

    helper = FormHelper()
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    helper.form_tag = False
    helper.form_show_errors = True

    excel_upload = forms.FileField(
        label='Excel file.',
        allow_empty_file=False,
        required=True,
        help_text='submit here a bank statement of contributions',
        widget=FileInput(attrs={
            'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel'}),
        validators=[FileValidator(
            max_size=FILE_UPLOAD_MAX_MEMORY_SIZE,
            allowed_extensions=['xls', 'xlsx'],
            allowed_mimetypes=[
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel',
                'application/vnd.ms-office',
            ],
            min_size=1)]
    )

    helper.layout = Layout(
        Field('excel_upload', css_class='input-sm form-control'),
        Hidden(name='identity', value=True, css_class='input-sm'),
    )


class InvestmentForm(ModelForm):

    helper = FormHelper()
    helper.form_tag = False
    helper.form_show_errors = True

    def __init__(self, *args, **kwargs):
        update = kwargs.pop(str('update'), None)

        super(InvestmentForm, self).__init__(*args, **kwargs)
        if update is not None and update is True:
            self.__update_form()
        else:
            self.__new_form()

    def __update_form(self):

        self.helper.layout = Layout(
            Fieldset(
                "General Details",
                Div(PrependedText('create_date', '<i class="fa fa-calendar"></i>', css_class='input-sm date-input'),
                    css_class='col-sm-12'),
                Div(PrependedText('project_name', 'ABC', css_class='input-sm'), css_class='col-sm-6'),
                Div(Field('project_manager', css_class='input-sm'), css_class='col-sm-6'),
                Div(Field('project_team', css_class='input-sm'), css_class='col-sm-12'),
                Div(PrependedText('start_date', '<i class="fa fa-calendar"></i>', css_class='input-sm date-input'),
                    css_class='col-sm-6'),
                Div(PrependedText('project_age', '<i class="fa fa-calendar"></i>', css_class='input-sm'),
                    css_class='col-sm-6'),
                Div(PrependedText('total_capital_invested', "UGX", css_class='input-sm'), css_class='col-sm-6'),
                Div(PrependedText('amount_returned', 'UGX', css_class='input-sm'), css_class='col-sm-6'),
                Div(PrependedText('interest', "UGX", css_class='input-sm'), css_class='col-sm-6'),
                Div(PrependedText('loss', "UGX", css_class='input-sm'), css_class='col-sm-6'),

                HTML(
                    '<div class="col-sm-12 col-md-12">'
                    '<div class="row slider-rate">'
                    '<div class="col-sm-1" ><span id="valuestart">0%</span> </div>'
                    '<div id="slider" class="col-sm-10" ></div>'
                    '<div class="col-sm-1" > <span id="valuestop">100%</span></div>'
                    '</div>'
                    '</div>'
                ),
                Div(PrependedText('project_rating', '<i class="fa fa-star"></i> <i class="fa fa-star"></i>',
                                  css_class='input-sm'), css_class='col-sm-6 col-md-6'),
                Div(Field('project_status', css_class='input-sm'), css_class='col-sm-6 col-md-6'),
                Div(Field('description', css_class='input-md'), css_class='col-sm-12 col-md-12'),
                Div(Fieldset(
                    "Summary",
                    TabHolder(
                        Tab('Highlights', 'positive_highlights'),
                        Tab('Challenges', 'challenges'),
                        Tab('Lessons', 'lessons_learnt'),
                        Tab('Way Foward', 'way_foward'),
                    )
                ), css_class='col-sm-12 col-md-12')
            )
        )

    def __new_form(self):
        self.helper.layout = Layout(
            Fieldset(
                "General Details",
                Div(PrependedText('create_date', '<i class="fa fa-calendar"></i>', css_class='input-sm date-input'),
                    css_class='col-sm-12'),
                Div(PrependedText('project_name', 'ABC', css_class='input-sm'), css_class='col-sm-6'),
                Div(Field('project_manager', css_class='input-sm'), css_class='col-sm-6'),
                Div(Field('project_team', css_class='input-sm'), css_class='col-sm-12'),
                Div(PrependedText('start_date', '<i class="fa fa-calendar"></i>', css_class='input-sm date-input'),
                    css_class='col-sm-6'),
                Div(PrependedText('project_age', '<i class="fa fa-calendar"></i>', css_class='input-sm'),
                    css_class='col-sm-6'),
                Div(PrependedText('total_capital_invested', "UGX", css_class='input-sm'), css_class='col-sm-6'),
                Div(Field('project_status', css_class='input-sm'), css_class='col-sm-6 col-md-6'),
                Div(Field('description', css_class='input-md'), css_class='col-sm-12 col-md-12'),
                Div(Fieldset(
                    "Summary",
                    TabHolder(
                        Tab('Highlights', 'positive_highlights'),
                        Tab('Challenges', 'challenges'),
                        Tab('Lessons', 'lessons_learnt'),
                        Tab('Way Foward', 'way_foward'),
                    )
                ), css_class='col-sm-12 col-md-12')
            )
        )

    def add_hidden(self, ids):
        hidden = Hidden(name='hidden_investment', value=ids, css_class='input-sm')
        self.helper.add_input(hidden)

    def readonly(self):
        self.fields['amount_returned'].widget.attrs['readonly'] = True
        self.fields['interest'].widget.attrs['readonly'] = True
        self.fields['loss'].widget.attrs['readonly'] = True

    class Meta:
        model = Investment
        fields = '__all__'
        widgets = {
            'project_rating': TextInput(attrs={'readonly': 'readonly'}),
            'description': TextInput(),
            'create_date': DateTimeInput(attrs={'readonly': True}),
        }


class InvestmentFinancialStatementForm(ModelForm):

    class Meta:
        model = InvestmentFinancialStatement
        fields = '__all__'
        widgets = {
            'particulars': TextInput(),
            'investment': Select(attrs={'class': 'input-sm investment-selection'}),
            'date': DateTimeInput(attrs={'class': 'input-sm date-input', 'placeholder': 'YYY-MM-DD HH:mm:ss'}),
        }


class InterestForm(ModelForm):

    helper = FormHelper()
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    helper.form_tag = False
    helper.form_show_errors = True

    helper.layout = Layout(
        AppendedText('interest', '%', css_class='input-sm'),
        Hidden(name='hidden_interest', value=1, css_class='input-sm'),
    )

    class Meta:
        model = Interest
        fields = '__all__'


class LoanForm(ModelForm):

    helper = FormHelper()
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    helper.form_tag = False
    helper.form_show_errors = True

    helper.layout = Layout(
        Fieldset(
            'Narative',
            Field('user', css_class='input-sm'),
            PrependedText('loan_date', '<i class="fa fa-calendar"></i>', css_class='input-sm date-input'),
            PrependedText('loan_duration', '123', css_class='input-sm'),
            Field('loan_status', css_class='input-sm'),
        ),
        Fieldset(
            'Amount (UGX)',
            PrependedText('loan_amount', 'UGX', css_class='input-sm'),
            PrependedText('loan_interest', 'UGX', css_class='input-sm'),
            PrependedText('total_amount', 'UGX', css_class='input-sm'),
            PrependedText('profit_earned', 'UGX', css_class='input-sm'),
            Fieldset(
                'payments',
                PrependedText('amount_paid', 'UGX', css_class='input-sm'),
                PrependedText('sur_charge', 'UGX', css_class='input-sm'),
                PrependedText('sub_total', 'UGX', css_class='input-sm'),
                PrependedText('outstanding_balance', 'UGX', css_class='input-sm'),
            )
        ),
    )

    def add_hidden(self, ids):
        hidden = Hidden(name='hidden_loan', value=ids, css_class='input-sm')
        self.helper.add_input(hidden)

    class Meta:
        model = Loan
        fields = '__all__'
        widgets = {
            'loan_interest': NumberInput(attrs={'readonly': True}),
            'total_amount': NumberInput(attrs={'readonly': True}),
            'outstanding_balance': NumberInput(attrs={'readonly': True}),
            'profit_earned': NumberInput(attrs={'readonly': True}),
            'amount_paid': NumberInput(attrs={'readonly': True}),
            'sub_total': NumberInput(attrs={'readonly': True}),
        }


class LoanPaymentForm(ModelForm):

    class Meta:
        model = LoanPayment
        fields = '__all__'
        widgets = {
            'loan': Select(attrs={'class': 'input-sm loan-selection'}),
            'pay_date': DateTimeInput(attrs={'class': 'input-sm date-input', 'placeholder': 'YYY-MM-DD HH:mm:ss'}),
        }
