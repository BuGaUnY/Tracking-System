# Generated by Django 4.1.5 on 2025-02-04 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0005_activity_organizer6_activity_organizer7_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancecheckin',
            name='date_checkin',
            field=models.DateField(null=True),
        ),
    ]
