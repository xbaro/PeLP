# Generated by Django 3.2.8 on 2021-10-17 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_alter_execution_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmodule',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'STATIC LIBRARY')], default=0),
        ),
    ]