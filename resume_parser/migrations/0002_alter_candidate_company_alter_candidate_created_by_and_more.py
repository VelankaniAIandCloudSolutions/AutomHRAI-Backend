# Generated by Django 4.2.11 on 2024-04-18 07:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resume_parser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='app_settings.company'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_creators', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='resume',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='app_settings.company'),
        ),
        migrations.AlterField(
            model_name='resume',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_creators', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='resume',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updates', to=settings.AUTH_USER_MODEL),
        ),
    ]
