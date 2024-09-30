# Generated by Django 3.2.8 on 2022-01-21 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0063_faq_full_text_index'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faq',
            name='content',
        ),
        migrations.RemoveField(
            model_name='faq',
            name='title',
        ),
        migrations.AddField(
            model_name='translatefaqtag',
            name='language',
            field=models.CharField(choices=[('ca', 'Catalan'), ('es', 'Spanish'), ('en', 'English')], default='en', max_length=5),
            preserve_default=False,
        ),
    ]
