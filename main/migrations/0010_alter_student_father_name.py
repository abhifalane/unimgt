# Generated by Django 5.2.1 on 2025-07-20 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_student_category_student_exam_date_student_exam_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='father_name',
            field=models.CharField(max_length=200),
        ),
    ]
