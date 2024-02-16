# Generated by Django 3.2.5 on 2024-01-22 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0002_auto_20240122_1554'),
        ('resume_parser', '0002_auto_20240122_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='candidate', to='app_settings.company'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='resume',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='candidates', to='resume_parser.resume'),
        ),
        migrations.AlterField(
            model_name='resume',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resume', to='app_settings.company'),
        ),
    ]