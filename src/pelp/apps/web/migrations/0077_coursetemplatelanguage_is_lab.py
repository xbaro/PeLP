# Generated by Django 3.2.12 on 2023-10-10 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0076_coursetemplate_coursetemplatelanguage'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursetemplatelanguage',
            name='is_lab',
            field=models.BooleanField(default=False),
        ),
    ]