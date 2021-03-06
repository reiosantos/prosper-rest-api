# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-08-09 12:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import home.support.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('finance', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='user',
            field=models.ForeignKey(default=home.support.validators.get_id, help_text='user taking loan', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='account_id'),
        ),
        migrations.AddField(
            model_name='investmentfinancialstatement',
            name='investment',
            field=models.ForeignKey(default=home.support.validators.get_id, help_text='select the investment under progress', on_delete=django.db.models.deletion.CASCADE, to='finance.Investment'),
        ),
        migrations.AddField(
            model_name='investment',
            name='project_manager',
            field=models.ForeignKey(default=home.support.validators.get_id, on_delete=django.db.models.deletion.CASCADE, related_name='project_man', to=settings.AUTH_USER_MODEL, to_field='account_id'),
        ),
        migrations.AddField(
            model_name='investment',
            name='project_team',
            field=models.ManyToManyField(blank=True, help_text='Select specific members for this project.', related_name='team_members', to=settings.AUTH_USER_MODEL, verbose_name='team members'),
        ),
        migrations.AddField(
            model_name='contribution',
            name='user',
            field=models.ForeignKey(default=home.support.validators.get_id, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='account_id'),
        ),
    ]
