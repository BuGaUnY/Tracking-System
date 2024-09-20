# Generated by Django 4.1.5 on 2024-09-11 18:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('att_name', models.CharField(default='default_value', max_length=50)),
                ('credits', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ],
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(default='organizer-image/default.png', upload_to='organizer-image')),
                ('website', models.URLField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='base.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('image', models.ImageField(default='', upload_to='event-image')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('detail', models.TextField()),
                ('activity_category', models.CharField(blank=True, choices=[('กิจกรรมพิเศษ', 'กิจกรรมพิเศษ'), ('กิจกรรมเข้าแถว', 'กิจกรรมเข้าแถว'), ('กิจกรรมชมรม', 'กิจกรรมชมรม'), ('กิจกรรมโฮมรูม', 'กิจกรรมโฮมรูม'), ('กิจกรรมลูกเสือ', 'กิจกรรมลูกเสือ'), ('กิจกรรม ร.ด.', 'กิจกรรม ร.ด.')], max_length=20, null=True)),
                ('date_start', models.DateTimeField(blank=True, null=True)),
                ('status', models.BooleanField(default=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('organizer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='activity.organizer')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('first_name', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('room', models.CharField(max_length=10, null=True)),
                ('degree', models.CharField(max_length=20, null=True)),
                ('department', models.CharField(max_length=100, null=True)),
                ('checkin', models.BooleanField(default=False)),
                ('qrcode', models.ImageField(blank=True, default='', null=True, upload_to='ticket-qrcode')),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('activity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='activity.activity')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ticket_profile', to='base.profile')),
            ],
            options={
                'unique_together': {('activity', 'profile')},
            },
        ),
        migrations.CreateModel(
            name='AttendanceCheckin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('student_number', models.CharField(blank=True, max_length=20, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('room', models.CharField(blank=True, max_length=10, null=True)),
                ('degree', models.CharField(blank=True, max_length=10, null=True)),
                ('department', models.CharField(blank=True, max_length=50, null=True)),
                ('date_checkin', models.DateTimeField(blank=True, null=True)),
                ('presence', models.IntegerField(default=1)),
                ('att_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='activity.attendance')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_profile', to='base.profile')),
            ],
            options={
                'unique_together': {('user', 'att_name')},
            },
        ),
    ]
