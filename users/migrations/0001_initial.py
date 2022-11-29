# Generated by Django 4.1.3 on 2022-11-29 10:50

from django.db import migrations, models
import users.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.IntegerField(choices=[(1, 'Main administrator'), (2, 'Administrator'), (3, 'Curator'), (4, 'Learner')], default=3, verbose_name='role')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('password', models.CharField(blank=True, max_length=120, null=True, verbose_name='password')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='phone number')),
                ('google', models.CharField(blank=True, max_length=40, null=True, verbose_name='google account')),
                ('facebook', models.CharField(blank=True, max_length=40, null=True, verbose_name='facebook account')),
                ('last_login', models.DateTimeField(auto_now_add=True, verbose_name='last login date')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='join date')),
                ('is_active', models.BooleanField(default=False, verbose_name='is active')),
                ('security_code', models.CharField(blank=True, max_length=6, null=True, verbose_name='security code')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', users.managers.UserManager()),
            ],
        ),
    ]
