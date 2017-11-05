from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class ClubDetails(models.Model):

    start_date = models.DateTimeField('Start date', auto_now=False, default=timezone.now)
    monthly_contribution = models.DecimalField('Monthly Pay.', max_digits=12, decimal_places=2, default=0,
                                               validators=[
                                                   MinValueValidator(Decimal('00.00')),
                                               ])

    def __unicode__(self):
        return self.monthly_contribution

    class Meta:
        default_permissions = ('modify',)


class Expenses(models.Model):

    date = models.DateTimeField('Date', auto_now=False, default=timezone.now)
    particulars = models.CharField(max_length=255, blank=False, )
    invested = models.DecimalField('Invested.', max_digits=12, decimal_places=2, default=0,
                                               validators=[
                                                   MinValueValidator(Decimal('00.00')),
                                               ])
    recouped = models.DecimalField('Recouped.', max_digits=12, decimal_places=2, default=0,
                                               validators=[
                                                   MinValueValidator(Decimal('00.00')),
                                               ])
    interest = models.DecimalField('Interest.', max_digits=12, decimal_places=2, default=0,
                                   validators=[
                                       MinValueValidator(Decimal('00.00')),
                                   ])

    def __unicode__(self):
        return self.particulars

    class Meta:
        default_permissions = ('modify',)