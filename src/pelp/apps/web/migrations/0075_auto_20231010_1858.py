# Generated by Django 3.2.12 on 2023-10-10 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0074_faqrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursegroup',
            name='sis_code',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='translatecourse',
            name='sis_code',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
