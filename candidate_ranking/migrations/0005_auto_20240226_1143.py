# Generated by Django 3.2.5 on 2024-02-26 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0002_auto_20240122_1554'),
        ('candidate_ranking', '0004_auto_20240226_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='department', to='app_settings.company'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='entity', to='app_settings.company'),
        ),
    ]