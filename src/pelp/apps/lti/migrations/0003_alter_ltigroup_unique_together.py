# Generated by Django 3.2.8 on 2021-11-04 00:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lti', '0002_alter_lticonsumerproperties_consumer'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ltigroup',
            unique_together={('consumer', 'group_code')},
        ),
    ]
