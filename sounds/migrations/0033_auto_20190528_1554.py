# Generated by Django 1.11.20 on 2019-05-28 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sounds', '0032_auto_20180905_1301'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bulkuploadprogress',
            options={'permissions': (('can_describe_in_bulk', 'Can use the Bulk Describe feature.'),)},
        ),
    ]
