# Generated by Django 4.1.3 on 2022-12-13 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_rename_access_course_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
