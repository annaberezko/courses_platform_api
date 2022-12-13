# Generated by Django 4.1.3 on 2022-12-12 11:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import lessons.models
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0004_rename_access_course_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='lesson name')),
                ('video', models.CharField(blank=True, max_length=100, null=True, verbose_name='video link')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('home_task', models.TextField(blank=True, null=True)),
                ('tests_task', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=120, verbose_name='lesson name')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.lesson')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.CharField(max_length=100, verbose_name='test option')),
                ('correct', models.BooleanField(default=False)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.test')),
            ],
        ),
        migrations.CreateModel(
            name='Materials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=lessons.models.Materials.file_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg', 'pdf']), users.validators.validate_size])),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.lesson')),
            ],
        ),
    ]
