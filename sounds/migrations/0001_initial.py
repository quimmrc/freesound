# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-14 10:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('apiv2', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('geotags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedSound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sound_id', models.IntegerField(db_index=True, default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('reason_type', models.CharField(choices=[(b'O', 'Offending sound'), (b'I', 'Illegal sound'), (b'T', 'Other problem')], default=b'I', max_length=1)),
                ('reason', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('reporting_user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(editable=False)),
                ('name', models.CharField(max_length=512)),
                ('abbreviation', models.CharField(db_index=True, max_length=8)),
                ('summary', models.TextField()),
                ('deed_url', models.URLField()),
                ('legal_code_url', models.URLField()),
                ('is_public', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('is_dirty', models.BooleanField(db_index=True, default=False)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('license_crc', models.CharField(blank=True, max_length=8)),
                ('last_updated', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('num_downloads', models.PositiveIntegerField(default=0)),
                ('num_sounds', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RemixGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protovis_data', models.TextField(blank=True, default=None, null=True)),
                ('group_size', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Sound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('original_filename', models.CharField(max_length=512)),
                ('original_path', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('base_filename_slug', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('description', models.TextField()),
                ('date_recorded', models.DateField(blank=True, default=None, null=True)),
                ('type', models.CharField(choices=[(b'wav', b'Wave'), (b'ogg', b'Ogg Vorbis'), (b'aiff', b'AIFF'), (b'mp3', b'Mp3'), (b'flac', b'Flac')], db_index=True, max_length=4)),
                ('duration', models.FloatField(default=0)),
                ('bitrate', models.IntegerField(default=0)),
                ('bitdepth', models.IntegerField(blank=True, default=None, null=True)),
                ('samplerate', models.FloatField(default=0)),
                ('filesize', models.IntegerField(default=0)),
                ('channels', models.IntegerField(default=0)),
                ('md5', models.CharField(db_index=True, max_length=32, unique=True)),
                ('crc', models.CharField(blank=True, max_length=8)),
                ('moderation_state', models.CharField(choices=[(b'PE', 'Pending'), (b'OK', 'OK'), (b'DE', 'Deferred')], db_index=True, default=b'PE', max_length=2)),
                ('moderation_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('moderation_note', models.TextField(blank=True, default=None, null=True)),
                ('has_bad_description', models.BooleanField(default=False)),
                ('processing_state', models.CharField(choices=[(b'PE', 'Pending'), (b'OK', 'OK'), (b'FA', 'Failed')], db_index=True, default=b'PE', max_length=2)),
                ('processing_ongoing_state', models.CharField(choices=[(b'NO', 'None'), (b'QU', 'Queued'), (b'PR', 'Processing'), (b'FI', 'Finished')], db_index=True, default=b'NO', max_length=2)),
                ('processing_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('processing_log', models.TextField(blank=True, default=None, null=True)),
                ('is_index_dirty', models.BooleanField(default=True)),
                ('similarity_state', models.CharField(choices=[(b'PE', 'Pending'), (b'OK', 'OK'), (b'FA', 'Failed')], db_index=True, default=b'PE', max_length=2)),
                ('analysis_state', models.CharField(choices=[(b'PE', 'Pending'), (b'OK', 'OK'), (b'FA', 'Failed')], db_index=True, default=b'PE', max_length=2)),
                ('num_comments', models.PositiveIntegerField(default=0)),
                ('num_downloads', models.PositiveIntegerField(default=0)),
                ('avg_rating', models.FloatField(default=0)),
                ('num_ratings', models.PositiveIntegerField(default=0)),
                ('geotag', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='geotags.GeoTag')),
                ('license', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sounds.License')),
                ('pack', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sounds.Pack')),
                ('sources', models.ManyToManyField(blank=True, related_name='remixes', to='sounds.Sound')),
                ('uploaded_with_apiv2_client', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apiv2.ApiV2Client')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sounds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='remixgroup',
            name='sounds',
            field=models.ManyToManyField(blank=True, related_name='remix_group', to='sounds.Sound'),
        ),
        migrations.AddField(
            model_name='flag',
            name='sound',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sounds.Sound'),
        ),
        migrations.AddField(
            model_name='download',
            name='pack',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='sounds.Pack'),
        ),
        migrations.AddField(
            model_name='download',
            name='sound',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='sounds.Sound'),
        ),
        migrations.AddField(
            model_name='download',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='pack',
            unique_together=set([('user', 'name')]),
        ),
    ]
