# Generated by Django 3.1.2 on 2020-11-25 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_classe_credit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classe',
            name='credit',
            field=models.IntegerField(),
        ),
    ]