# Generated by Django 3.2.8 on 2021-10-30 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0037_learnerresult_test_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='learnerresult',
            name='built',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='num_test_failed',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='num_test_passed',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='num_tests',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
