# Generated by Django 3.2.8 on 2021-10-18 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0016_projecttest_submissiontestresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='projecttest',
            name='grouping_node',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submissiontestresult',
            name='num_failed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='submissiontestresult',
            name='num_passed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='submissiontestresult',
            name='num_tests',
            field=models.IntegerField(default=0),
        ),
    ]
