# Generated by Django 3.0.7 on 2021-01-19 01:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0002_auto_20210115_1428'),
    ]

    operations = [
        migrations.CreateModel(
            name='Legend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.TextField(null=True)),
                ('datetimes', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('cardata', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interface.CarDataModel')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterField(
            model_name='dtgdatamodel',
            name='oplog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='interface.Legend'),
        ),
    ]
