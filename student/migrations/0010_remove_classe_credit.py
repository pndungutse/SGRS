# Generated by Django 3.1.2 on 2020-11-30 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0009_auto_20201125_1707'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classe',
            name='credit',
        ),
    ]
