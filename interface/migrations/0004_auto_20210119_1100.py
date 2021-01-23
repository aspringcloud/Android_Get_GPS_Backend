# Generated by Django 3.0.7 on 2021-01-19 02:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0003_auto_20210119_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtgdatamodel',
            name='Legend',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='interface.Legend'),
        ),
        migrations.AlterField(
            model_name='dtgdatamodel',
            name='oplog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dtgdatas_to_oplog', related_query_name='oplog_to_dtgdata', to='interface.OperationLogModel'),
        ),
    ]