# Generated by Django 3.2.8 on 2021-10-15 10:33

from django.db import migrations, models
import django.db.models.deletion
import pelp.apps.web.models.project
import pelp.apps.web.models.project_file
import pelp.apps.web.models.submission
import pelp.apps.web.models.submission_file


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GitRepository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('base_url', models.CharField(max_length=255)),
                ('username', models.CharField(default=None, max_length=255, null=True)),
                ('token', models.CharField(default=None, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Learner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('courses', models.ManyToManyField(to='web.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, 'CREATED'), (1, 'UPLOADED'), (2, 'CLONED'), (3, 'VALID'), (4, 'TESTING'), (5, 'PROCESSED'), (6, 'INVALID'), (7, 'ERROR'), (8, 'TIMEOUT')], default=0)),
                ('executable_name', models.CharField(max_length=255)),
                ('test_arguments', models.CharField(max_length=255)),
                ('results_path', models.CharField(max_length=255)),
                ('image', models.CharField(max_length=255)),
                ('anchor_file', models.CharField(default=None, max_length=255, null=True)),
                ('allowed_files_regex', models.CharField(default=None, max_length=255, null=True)),
                ('repository_url', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('repository_base_branch', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('repository_test_branch', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('code_base_zip', models.FileField(blank=True, default=None, max_length=250, null=True, upload_to=pelp.apps.web.models.project.get_base_code_upload_path)),
                ('code_test_zip', models.FileField(blank=True, default=None, max_length=250, null=True, upload_to=pelp.apps.web.models.project.get_test_code_upload_path)),
                ('max_execution_time', models.IntegerField(default=120)),
                ('mem_limit', models.CharField(default='10m', max_length=15)),
                ('activity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='web.activity')),
                ('repository', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='web.gitrepository')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('base_path', models.CharField(max_length=255)),
                ('allowed_files_regex', models.CharField(default=None, max_length=255, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.project')),
            ],
            options={
                'unique_together': {('project', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, 'CREATED'), (1, 'UPLOADED'), (2, 'CHECKING'), (3, 'VALID'), (4, 'TESTING'), (5, 'PROCESSED'), (6, 'INVALID'), (7, 'ERROR'), (8, 'TIMEOUT')], default=0)),
                ('repository', models.CharField(default=None, max_length=255, null=True)),
                ('submitted_at', models.DateTimeField(default=None, null=True)),
                ('executed_at', models.DateTimeField(default=None, null=True)),
                ('elapsed_time', models.IntegerField(default=None, null=True)),
                ('result', models.TextField(blank=True, default=None, null=True)),
                ('test_passed', models.BooleanField(default=None, null=True)),
                ('test_percentage', models.FloatField(default=None, null=True)),
                ('submission', models.FileField(blank=True, null=True, upload_to=pelp.apps.web.models.submission.get_submission_upload_path)),
                ('merged_submission', models.FileField(blank=True, null=True, upload_to=pelp.apps.web.models.submission.get_submission_upload_path)),
                ('execution_logs', models.FileField(blank=True, null=True, upload_to=pelp.apps.web.models.submission.get_logs_upload_path)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.activity')),
                ('learner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.learner')),
            ],
        ),
        migrations.CreateModel(
            name='TestSubmission',
            fields=[
                ('submission_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web.submission')),
            ],
            bases=('web.submission',),
        ),
        migrations.CreateModel(
            name='SubmissionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, 'ADDED'), (1, 'SKIPPED'), (2, 'FILTERED')], default=0)),
                ('filename', models.CharField(default=None, max_length=255, null=True)),
                ('original_filename', models.CharField(default=None, max_length=255, null=True)),
                ('file', models.FileField(upload_to=pelp.apps.web.models.submission_file.get_submission_file_upload_path)),
                ('module', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web.projectmodule')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.submission')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(default=None, max_length=255, null=True)),
                ('original_filename', models.CharField(default=None, max_length=255, null=True)),
                ('file', models.FileField(upload_to=pelp.apps.web.models.project_file.get_project_file_upload_path)),
                ('locked', models.BooleanField(default=True)),
                ('module', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='web.projectmodule')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.project')),
            ],
        ),
        migrations.CreateModel(
            name='Execution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('container_id', models.CharField(max_length=255)),
                ('started_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='web.project')),
                ('submission', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.submission')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.semester'),
        ),
        migrations.AddField(
            model_name='activity',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.course'),
        ),
        migrations.AddField(
            model_name='project',
            name='code_test_result',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='web.testsubmission'),
        ),
        migrations.AlterUniqueTogether(
            name='activity',
            unique_together={('course', 'code')},
        ),
    ]