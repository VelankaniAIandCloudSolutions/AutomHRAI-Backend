# Generated by Django 4.2.11 on 2024-06-13 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='cut_off_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]