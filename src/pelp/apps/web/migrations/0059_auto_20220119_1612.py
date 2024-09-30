# Generated by Django 3.2.8 on 2022-01-19 15:12

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0058_activityfeedback_is_np'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FaqTag',
            fields=[
                ('tag', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TranslateFaqTag',
            fields=[
                ('tag', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('faqtag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.faqtag')),
            ],
        ),
        migrations.CreateModel(
            name='TranslateFaq',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('ca', 'Catalan'), ('es', 'Spanish'), ('en', 'English')], max_length=5)),
                ('title', models.CharField(max_length=255)),
                ('content', ckeditor_uploader.fields.RichTextUploadingField()),
                ('faq', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.faq')),
            ],
        ),
        migrations.AddField(
            model_name='faq',
            name='tags',
            field=models.ManyToManyField(to='web.FaqTag'),
        ),
    ]