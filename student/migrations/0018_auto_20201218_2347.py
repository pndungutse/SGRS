# Generated by Django 3.1.2 on 2020-12-18 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0017_district_profile_pc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student_course',
            name='final_marks',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='student_course',
            name='mid_marks',
            field=models.FloatField(null=True),
        ),
    ]
