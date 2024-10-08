# Generated by Django 3.2.8 on 2021-10-16 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20211016_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='execution',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'CREATING'), (1, 'CREATED'), (2, 'PREPARING'), (3, 'PREPARED'), (4, 'RUNNING'), (5, 'FINISHED'), (6, 'INVALID'), (7, 'ERROR'), (8, 'TIMEOUT')], default=0),
        ),
    ]
