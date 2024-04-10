# Generated by Django 3.2.5 on 2024-02-26 06:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_settings', '0003_auto_20240226_1212'),
        ('candidate_ranking', '0005_auto_20240226_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='departments', to='app_settings.entity'),
        ),
        migrations.DeleteModel(
            name='Entity',
        ),
    ]