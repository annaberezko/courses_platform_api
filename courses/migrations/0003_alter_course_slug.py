# Generated by Django 4.1.3 on 2022-12-06 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_course_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=models.SlugField(max_length=20, unique=True, verbose_name='slug'),
        ),
    ]
