# Generated by Django 3.1.2 on 2020-11-02 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student_Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid_marks', models.FloatField()),
                ('final_marks', models.FloatField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student')),
            ],
        ),
    ]