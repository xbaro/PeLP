# Generated by Django 3.2.8 on 2022-01-20 13:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0060_auto_20220120_1428'),
    ]

    operations = [
        migrations.RunSQL(
            ('CREATE FULLTEXT INDEX faq_text_index ON web_faq (title, content)',),
            ('DROP INDEX faq_text_index on web_faq',)
        ),
    ]
