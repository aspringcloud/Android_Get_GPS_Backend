# Generated by Django 3.0.7 on 2021-01-14 06:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0001_initial'),
        ('gps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gps',
            name='oplog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gps_to_oplog', related_query_name='gps_to_dtgdata', to='interface.OperationLogModel'),
        ),
    ]
