# Generated by Django 3.0.7 on 2021-01-14 06:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gps', '0002_gps_oplog'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gps',
            old_name='created',
            new_name='datetimes',
        ),
    ]
