# Generated by Django 3.2.5 on 2024-04-17 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_useraccount_sbu_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useraccount',
            old_name='sbu_category',
            new_name='sub_category',
        ),
    ]
