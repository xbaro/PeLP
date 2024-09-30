# Generated by Django 3.2.8 on 2022-01-20 13:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0061_faq_full_text_index'),
    ]

    operations = [
        migrations.RunSQL(
            ('CREATE FULLTEXT INDEX trans_faq_text_index ON web_translatefaq (title, content)',),
            ('DROP INDEX trans_faq_text_index on web_translatefaq',)
        ),
    ]
