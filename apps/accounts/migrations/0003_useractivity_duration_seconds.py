# Migration: add duration_seconds field to UserActivity (tracks time spent in app per day)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_passwordresettoken_useractivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivity',
            name='duration_seconds',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
