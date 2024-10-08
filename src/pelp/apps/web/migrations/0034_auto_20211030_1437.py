# Generated by Django 3.2.8 on 2021-10-30 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0033_alter_mailsubmission_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='progress_path',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='projecttest',
            name='weight',
            field=models.FloatField(default=1.0),
        ),
        migrations.AddField(
            model_name='submission',
            name='built',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='correct_execution',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='metadata',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='progress',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='submissiontestresult',
            name='compiled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submissiontestresult',
            name='total_weight',
            field=models.FloatField(default=0.0),
        ),
    ]
