# Generated by Django 1.11 on 2018-09-05 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sounds', '0031_soundanalysis'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='soundanalysis',
            unique_together={('sound', 'extractor')},
        ),
    ]
