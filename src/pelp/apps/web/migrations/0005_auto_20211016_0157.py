# Generated by Django 3.2.8 on 2021-10-15 23:57

from django.db import migrations, models
import pelp.apps.web.models.submission


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20211015_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='merged_submission',
            field=models.FileField(blank=True, null=True, upload_to=pelp.apps.web.models.submission.get_merged_submission_upload_path),
        ),
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'CREATING'), (1, 'CREATED'), (2, 'CLONING'), (3, 'CLONED'), (4, 'MERGING'), (5, 'MERGED'), (6, 'TESTING'), (7, 'PROCESSED'), (8, 'INVALID'), (9, 'ERROR'), (10, 'TIMEOUT')], default=0),
        ),
    ]
