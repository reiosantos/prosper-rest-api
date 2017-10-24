# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-12 17:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_status',
            field=models.CharField(choices=[('active', 'Active'), ('cancelled', 'Cancel Request'), ('deleted', 'Exited / delete'), ('pending', 'Pending Approval')], default='pending', help_text='select the current status of the user', max_length=255),
        ),
    ]
