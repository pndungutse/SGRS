# Generated by Django 3.1.2 on 2020-11-20 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_district_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student_course',
            name='final_marks',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='student_course',
            name='mid_marks',
            field=models.FloatField(default=0.0),
        ),
    ]
