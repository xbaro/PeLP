# Generated by Django 3.2.8 on 2021-12-20 18:03

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0044_submission_diff_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('general', ckeditor.fields.RichTextField(blank=True, default=None, null=True)),
                ('score', models.FloatField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('activity', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='web.activity')),
                ('instructor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='web.instructor')),
                ('learner', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='web.learner')),
            ],
            options={
                'unique_together': {('activity', 'learner')},
            },
        ),
    ]
