# Generated by Django 5.0.6 on 2025-02-20 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0049_employee_currentemployersection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employmenthistory',
            name='end_date',
        ),
        migrations.AddField(
            model_name='employmenthistory',
            name='employer_section_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.sections', verbose_name='القسم'),
        ),
    ]
