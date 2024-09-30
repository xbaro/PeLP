# Generated by Django 3.2.8 on 2021-10-17 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_projectmodule_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learner',
            name='courses',
        ),
        migrations.CreateModel(
            name='CourseGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('locale', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.course')),
            ],
        ),
        migrations.AddField(
            model_name='learner',
            name='groups',
            field=models.ManyToManyField(to='web.CourseGroup'),
        ),
    ]