from django.contrib import admin

from finance.models import Contribution, Investment, InvestmentFinancialStatement

admin.site.register(Contribution)
admin.site.register(Investment)
admin.site.register(InvestmentFinancialStatement)