# Generated by Django 3.2.8 on 2021-10-26 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0025_alter_learnerresult_error'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailInbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('max_submissions', models.IntegerField(default=10)),
                ('max_submissions_day', models.IntegerField(default=2)),
                ('allow_user_replacement', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='web.activity')),
            ],
        ),
        migrations.CreateModel(
            name='MailSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('received_at', models.DateTimeField(default=None)),
                ('processed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('answered_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('message_id', models.IntegerField(default=None, unique=True)),
                ('replacement_mail', models.CharField(blank=True, default=None, max_length=250, null=True)),
                ('inbox', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='web.mailinbox')),
                ('instructor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.instructor')),
                ('learner', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='web.learner')),
                ('submission', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.submission')),
            ],
        ),
        migrations.CreateModel(
            name='InstructorMailSubmission',
            fields=[
                ('mailsubmission_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web.mailsubmission')),
            ],
            bases=('web.mailsubmission',),
        ),
        migrations.CreateModel(
            name='InstructorSubmission',
            fields=[
                ('submission_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web.submission')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.instructor')),
            ],
            bases=('web.submission',),
        ),
    ]
