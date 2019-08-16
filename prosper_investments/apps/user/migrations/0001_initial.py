# Generated by Django 2.2.3 on 2019-08-10 12:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('venue', '0001_initial'),
        ('permission', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_name', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('is_visible_to_all', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'psp_dashboard_sections',
            },
        ),
        migrations.CreateModel(
            name='TemporaryToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('service', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ge_temporary_token', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'psp_temporary_token',
            },
        ),
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'psp_api_key',
            },
        ),
        migrations.CreateModel(
            name='VenueViewerType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('permissions', models.ManyToManyField(to='permission.ContributionPermission')),
                ('sections', models.ManyToManyField(related_name='viewer_types', to='user.DashboardSection')),
                ('users', models.ManyToManyField(related_name='viewer_types', to=settings.AUTH_USER_MODEL)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venue.Venue')),
            ],
            options={
                'db_table': 'psp_venue_viewer_type',
                'unique_together': {('venue', 'name')},
            },
        ),
    ]