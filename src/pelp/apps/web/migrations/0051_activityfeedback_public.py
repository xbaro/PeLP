# Generated by Django 3.2.8 on 2022-01-07 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0050_translaterubricelement_translaterubricelementoption'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityfeedback',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
