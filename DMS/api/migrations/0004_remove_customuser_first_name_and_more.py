# Generated by Django 5.1.4 on 2025-01-27 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_excelfile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='last_name',
        ),
    ]
