# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-14 10:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('geotags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about', models.TextField(blank=True, default=None, null=True)),
                ('home_page', models.URLField(blank=True, default=None, null=True)),
                ('signature', models.TextField(blank=True, max_length=256, null=True)),
                ('has_avatar', models.BooleanField(default=False)),
                ('wants_newsletter', models.BooleanField(db_index=True, default=True)),
                ('is_whitelisted', models.BooleanField(db_index=True, default=False)),
                ('has_old_license', models.BooleanField(default=False)),
                ('not_shown_in_online_users_list', models.BooleanField(default=False)),
                ('accepted_tos', models.BooleanField(default=False)),
                ('enabled_stream_emails', models.BooleanField(db_index=True, default=False)),
                ('last_stream_email_sent', models.DateTimeField(db_index=True, default=None, null=True)),
                ('last_attempt_of_sending_stream_email', models.DateTimeField(db_index=True, default=None, null=True)),
                ('num_sounds', models.PositiveIntegerField(default=0, editable=False)),
                ('num_posts', models.PositiveIntegerField(default=0, editable=False)),
                ('geotag', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='geotags.GeoTag')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-user__date_joined',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResetEmailRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('reporting_user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-user__username',),
            },
        ),
    ]
