# Generated by Django 3.2.12 on 2023-10-12 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0077_coursetemplatelanguage_is_lab'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='template',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='web.coursetemplate'),
        ),
    ]
