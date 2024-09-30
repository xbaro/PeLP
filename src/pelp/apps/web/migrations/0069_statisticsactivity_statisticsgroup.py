# Generated by Django 3.2.8 on 2022-02-25 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0068_auto_20220223_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticsActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('learners', models.IntegerField()),
                ('learners_with_submissions', models.IntegerField(default=0)),
                ('mean_submissions_learner', models.IntegerField(default=0)),
                ('total_submissions', models.IntegerField(default=0)),
                ('score_np', models.IntegerField(default=0)),
                ('score_a', models.IntegerField(default=0)),
                ('score_b', models.IntegerField(default=0)),
                ('score_cp', models.IntegerField(default=0)),
                ('score_cm', models.IntegerField(default=0)),
                ('score_d', models.IntegerField(default=0)),
                ('has_evaluation', models.BooleanField(default=False)),
                ('eval_np', models.IntegerField(default=0)),
                ('eval_a', models.IntegerField(default=0)),
                ('eval_b', models.IntegerField(default=0)),
                ('eval_cp', models.IntegerField(default=0)),
                ('eval_cm', models.IntegerField(default=0)),
                ('eval_d', models.IntegerField(default=0)),
                ('metadata', models.TextField(blank=True, default=None, null=True)),
                ('activity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='web.activity')),
            ],
        ),
        migrations.CreateModel(
            name='StatisticsGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instructors', models.CharField(max_length=255)),
                ('locale', models.CharField(max_length=10)),
                ('learners', models.IntegerField()),
                ('learners_with_submissions', models.IntegerField(default=0)),
                ('mean_submissions_learner', models.IntegerField(default=0)),
                ('total_submissions', models.IntegerField(default=0)),
                ('score_np', models.IntegerField(default=0)),
                ('score_a', models.IntegerField(default=0)),
                ('score_b', models.IntegerField(default=0)),
                ('score_cp', models.IntegerField(default=0)),
                ('score_cm', models.IntegerField(default=0)),
                ('score_d', models.IntegerField(default=0)),
                ('has_evaluation', models.BooleanField(default=False)),
                ('eval_np', models.IntegerField(default=0)),
                ('eval_a', models.IntegerField(default=0)),
                ('eval_b', models.IntegerField(default=0)),
                ('eval_cp', models.IntegerField(default=0)),
                ('eval_cm', models.IntegerField(default=0)),
                ('eval_d', models.IntegerField(default=0)),
                ('metadata', models.TextField(blank=True, default=None, null=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.activity')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.coursegroup')),
            ],
            options={
                'unique_together': {('activity', 'group')},
            },
        ),
    ]
