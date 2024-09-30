# Generated by Django 3.2.8 on 2022-01-05 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0047_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'CREATING'), (1, 'CREATED'), (2, 'CLONING'), (3, 'CLONED'), (4, 'UPLOADING'), (5, 'UPLOADED'), (6, 'VALIDATING'), (7, 'VALID'), (8, 'TESTING'), (9, 'PROCESSED'), (10, 'INVALID'), (11, 'ERROR'), (12, 'TIMEOUT'), (13, 'FAILED_TEST')], default=0),
        ),
    ]