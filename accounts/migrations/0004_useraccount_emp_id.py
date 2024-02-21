
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_useraccount_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='emp_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
