# Generated by Django 2.2.7 on 2019-11-16 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20191115_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateprofile',
            name='is_employer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employerprofile',
            name='is_candidate',
            field=models.BooleanField(default=False),
        ),
    ]
