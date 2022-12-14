# Generated by Django 4.1.3 on 2022-12-04 16:45

import courses.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='course name')),
                ('cover', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to=courses.models.Course.file_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'png', 'jpeg'])])),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('sequence', models.BooleanField(default=False, verbose_name='sequence tasks')),
                ('access', models.BooleanField(default=True, verbose_name='is active')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField(auto_now_add=True)),
                ('date_end', models.DateField(blank=True, null=True)),
                ('access', models.BooleanField(default=False, verbose_name='is active')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
