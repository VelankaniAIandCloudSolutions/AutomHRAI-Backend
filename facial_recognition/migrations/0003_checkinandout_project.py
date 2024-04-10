# Generated by Django 3.2.5 on 2024-04-10 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20240410_1646'),
        ('facial_recognition', '0002_timesheet_break_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkinandout',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checks_project', to='accounts.project'),
        ),
    ]
