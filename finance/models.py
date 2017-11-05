
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy

from config.settings import FILE_UPLOAD_MAX_MEMORY_SIZE
from finance.support.support_functions import get_id
from finance.support.validators import FileValidator
from users.models import User


class Contribution(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=get_id, to_field='account_id')
    contribution_date = models.DateTimeField('deposit date', auto_now=False, default=timezone.now)
    deposit = models.DecimalField('deposit', max_digits=11, default=0, blank=False, decimal_places=2,
                                  help_text='your contribution this month')
    penalty = models.DecimalField('penalty', max_digits=11, default=0, decimal_places=2,
                                  help_text='charges deducted from this contribution')
    total = models.DecimalField('actual contribution',
                                max_digits=11, default=0, decimal_places=2,
                                help_text='Total amount contributed when charges are deducted')
    deposit_slip = models.FileField(db_column='deposit slip',
                                    validators=[
                                        FileValidator(
                                            max_size=FILE_UPLOAD_MAX_MEMORY_SIZE,
                                            allowed_extensions=['pdf'],
                                            allowed_mimetypes=['application/pdf'], min_size=1)], blank=True,
                                    help_text='upload deposit slip if available.. Only .pdf files are allowed',
                                    upload_to='deposit_slips')

    def __unicode__(self):
        return self.user.__str__() + " | " + date.strftime(self.contribution_date, "%b. %d, %Y, %I:%M %P")

    class Meta:
        get_latest_by = 'contribution_date'
        ordering = ['-contribution_date', 'user']
        default_permissions = ('add', 'delete', 'modify', 'view')


class Investment(models.Model):
    PROJECT_STATUS = (
        ('in_progress', 'In Progress'),
        ('cancelled', 'Canceled'),
        ('completed', 'Completed'),
    )
    create_date = models.DateTimeField(u'Created on', auto_now=False, default=timezone.now)
    project_name = models.CharField(ugettext_lazy('Project name'), max_length=255, null=False, default='', blank=False)
    project_manager = models.ForeignKey(User, related_name='project_man', on_delete=models.SET_DEFAULT,
                                        default=get_id, to_field='account_id')
    project_team = models.ManyToManyField(User, verbose_name='team members', blank=True, related_name='team_members',
                                          help_text='Select specific members for this project.')
    start_date = models.DateTimeField('Project start date', auto_now=False, default=timezone.now)
    project_age = models.DecimalField('Project Age/Length (months)', max_digits=3, null=False, decimal_places=1,
                                      default=1)
    project_rating = models.DecimalField('Project Performance', max_digits=3, default=0, blank=True, decimal_places=1,
                                         help_text='please rate the project performance using the slider')
    project_status = models.CharField(max_length=255, help_text='select/update the current status of the project',
                                      default='in_progress', choices=PROJECT_STATUS)
    total_capital_invested = models.DecimalField('Total Capital Invested', max_digits=12, decimal_places=2, default=0)
    amount_returned = models.DecimalField('Amount Returned', max_digits=12, blank=True, decimal_places=2, default=0)
    interest = models.DecimalField('Interest', max_digits=12, blank=True, decimal_places=2, default=0)
    loss = models.DecimalField('Loss', max_digits=12, blank=True, decimal_places=2, default=0)
    description = models.TextField('Project Description', null=True, blank=True)

    positive_highlights = models.TextField('Positive highlights', blank=True)
    challenges = models.TextField('Challenges', blank=True,
                                  help_text='challenges/problems encountered while on this project')
    lessons_learnt = models.TextField('Lessons learnt', blank=True,
                                      help_text='new lessons learnt while on this project')
    way_foward = models.TextField('Way forward', blank=True,
                                  help_text='what do you conclude as a ay forward for the team/organisation')

    def __unicode__(self):
        return self.project_name

    class Meta:
        ordering = ['-start_date', 'project_name']
        default_permissions = ('add', 'delete', 'modify', 'view')


class InvestmentFinancialStatement(models.Model):

    investment = models.ForeignKey(Investment, on_delete=models.SET_DEFAULT, default=get_id,
                                   help_text='select the investment under progres')
    date = models.DateTimeField(u'Acttivity date', auto_now=False, default=timezone.now,
                                help_text='date of activity instantiation')
    particulars = models.TextField('particulars', default='', null=True, blank=True)
    amount_spent = models.DecimalField('Amount Spent', max_digits=12, decimal_places=2, default=0,
                                       help_text='How much was spent on this activity')
    amount_returned = models.DecimalField('Amount Returned', max_digits=12, decimal_places=2, default=0,
                                          help_text='How much is returned after the activity')
    cash_at_hand = models.DecimalField('Cash at hand', max_digits=12, decimal_places=2, default=0,
                                       help_text='Dry Cash currently available')

    def __unicode__(self):
        return self.particulars, ' | ', date.strftime(self.date, "%b. %d, %Y, %I:%M %P")

    class Meta:
        default_permissions = ('add', 'delete', 'modify', 'view')


class Interest(models.Model):

    interest = models.DecimalField('Interest Rate(%) monthly',
                                   validators=[
                                       MinValueValidator(Decimal('00.00')),
                                       MaxValueValidator(Decimal('100.0'))
                                   ],
                                   max_digits=4, decimal_places=1, default=0.0)

    def __unicode__(self):
        return str(self.interest) + "%"

    class Meta:
        default_permissions = ('add', 'modify')


class Loan(models.Model):
    LOAN_STATUS = (
        ('running', 'loan running'),
        ('cancelled', 'Canceled'),
        ('completed', 'Completed'),
    )
    loan_date = models.DateTimeField('loan date', auto_now=False, default=timezone.now,
                                     help_text='loan start date')
    user = models.ForeignKey(User, to_field='account_id', on_delete=models.SET_DEFAULT,
                             default=get_id, help_text='user taking loan')
    loan_duration = models.DecimalField('Loan Duration(months)', max_digits=3, decimal_places=1, default=1.0,
                                        validators=[
                                            MinValueValidator(Decimal('00.00')),
                                        ])
    loan_amount = models.DecimalField('Loan Amount', max_digits=12, decimal_places=2, default=0,
                                      validators=[
                                       MinValueValidator(Decimal('00.00')),
                                      ])
    amount_paid = models.DecimalField('Amount paid', max_digits=12, decimal_places=2, default=0,
                                      validators=[
                                          MinValueValidator(Decimal('00.00')),
                                      ])
    sur_charge = models.DecimalField('Sur charge.', max_digits=12, decimal_places=2, default=0,
                                     validators=[
                                         MinValueValidator(Decimal('00.00')),
                                     ])
    sub_total = models.DecimalField('Sub total.', max_digits=12, decimal_places=2, default=0,
                                    validators=[
                                        MinValueValidator(Decimal('00.00')),
                                    ])
    loan_interest = models.DecimalField('Interest Amount', max_digits=12, decimal_places=2, default=0,
                                        validators=[
                                            MinValueValidator(Decimal('00.00')),
                                        ])
    total_amount = models.DecimalField('Total Amount', max_digits=12, decimal_places=2, default=0,
                                       validators=[
                                           MinValueValidator(Decimal('00.00')),
                                       ])
    outstanding_balance = models.DecimalField('Outstanding Bal.', max_digits=12, decimal_places=2, default=0,
                                              validators=[
                                                  MinValueValidator(Decimal('00.00')),
                                              ])
    profit_earned = models.DecimalField('Profits', max_digits=12, decimal_places=2, default=0,
                                        validators=[
                                            MinValueValidator(Decimal('00.00')),
                                        ])
    loan_status = models.CharField(max_length=255, default='running', choices=LOAN_STATUS)

    def calculate_amounts(self, paid=None, rate=None):

        if paid is None or rate is None:
            return False

        self.amount_paid = paid

        if self.loan_duration <= 2:
            r = rate / 100
        else:
            r = rate + ((self.loan_duration-2) * 10)/100

        self.loan_interest = self.loan_amount * r
        self.total_amount = self.loan_amount + self.loan_interest
        self.outstanding_balance = self.total_amount - self.amount_paid
        self.sub_total = self.amount_paid + self.sur_charge
        self.profit_earned = 0

        if self.amount_paid >= self.total_amount:
            self.profit_earned = (self.amount_paid - self.loan_amount)+self.sur_charge

        return True

    def __unicode__(self):
        return self.user.__str__() + " | " + date.strftime(self.loan_date, "%b. %d, %Y, %I:%M %P")

    class Meta:
        ordering = ['-loan_date', 'total_amount']
        default_permissions = ('add', 'delete', 'modify', 'view')


class LoanPayment(models.Model):

    pay_date = models.DateTimeField('payment date', auto_now=False, default=timezone.now)
    loan = models.ForeignKey(Loan, on_delete=models.SET_DEFAULT, default=get_id, help_text='loan being repayed')
    paid_amount = models.DecimalField('Amount paid.', max_digits=12, decimal_places=2, default=0,
                                      validators=[
                                          MinValueValidator(Decimal('00.00')),
                                      ])

    def __unicode__(self):
        return self.loan

    class Meta:
        default_permissions = ('add', 'delete', 'modify', 'view')
