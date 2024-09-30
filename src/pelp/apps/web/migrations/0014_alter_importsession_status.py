# Generated by Django 3.2.8 on 2021-10-17 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_importsession_valid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importsession',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'CREATED'), (1, 'LOADING'), (2, 'LOADED'), (3, 'IMPORTING'), (4, 'IMPORTED'), (5, 'INVALID'), (6, 'ERROR')], default=0),
        ),
    ]
