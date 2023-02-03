# Generated by Django 1.11 on 2017-10-02 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sounds', '0011_auto_20170928_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sound',
            name='type',
            field=models.CharField(choices=[(b'wav', b'Wave'), (b'ogg', b'Ogg Vorbis'), (b'aiff', b'AIFF'), (b'mp3', b'Mp3'), (b'flac', b'Flac'), (b'm4a', b'M4a')], db_index=True, max_length=4),
        ),
    ]
