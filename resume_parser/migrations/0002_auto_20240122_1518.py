# Generated by Django 3.2.5 on 2024-01-22 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0001_initial'),
        ('resume_parser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_settings.company'),
        ),
        migrations.AddField(
            model_name='resume',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app_settings.company'),
        ),
    ]