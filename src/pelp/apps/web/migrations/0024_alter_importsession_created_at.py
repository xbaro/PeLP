# Generated by Django 3.2.8 on 2021-10-25 12:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0023_learnerresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsession',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
