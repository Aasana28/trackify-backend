# Migration: add remind_time and email_sent to Reminder

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reminders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reminder',
            name='remind_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reminder',
            name='email_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name='reminder',
            options={'ordering': ['date', 'remind_time']},
        ),
    ]
