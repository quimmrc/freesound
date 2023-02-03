# Generated by Django 1.11 on 2017-05-10 09:45

from django.db import migrations


def replace_empty_email_addresses(apps, schema_editor):
    User = apps.get_model("auth", "User")
    users = User.objects.filter(email="")
    for user in users:
        user.email = f'noemail+{user.username}@freesound.org'
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_sameuser'),
    ]

    # Add unique constraint to 'email' field in auth_user table
    operations = [
        migrations.RunPython(replace_empty_email_addresses, migrations.RunPython.noop),
        migrations.RunSQL('ALTER TABLE "auth_user" ADD CONSTRAINT "auth_user_email_uniq" UNIQUE ("email");'),
    ]
