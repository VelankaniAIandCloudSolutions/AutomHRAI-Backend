# Generated by Django 3.2.5 on 2024-04-15 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20240410_1853'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useraccount',
            old_name='addhar_card',
            new_name='aadhaar_card',
        ),
        migrations.RenameField(
            model_name='useraccount',
            old_name='is_contact_worker',
            new_name='is_contract_worker',
        ),
        migrations.RenameField(
            model_name='useraccount',
            old_name='is_superviser',
            new_name='is_supervisor',
        ),
    ]