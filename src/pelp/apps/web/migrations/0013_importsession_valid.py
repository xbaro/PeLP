# Generated by Django 3.2.8 on 2021-10-17 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_auto_20211017_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='importsession',
            name='valid',
            field=models.BooleanField(default=False),
        ),
    ]
