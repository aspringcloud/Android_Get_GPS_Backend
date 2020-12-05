from django.db import models
from django.conf import settings
from django.utils import timezone
import os


def get_date_path(filetype, car_num, data_date):
    now_day = data_date
    nowDate_year = now_day.strftime('%Y')
    nowDate_month = now_day.strftime('%m')
    nowDate_day = now_day.strftime('%d')
    return os.path.join(car_num, f'{nowDate_year}-{nowDate_month}', f'{nowDate_year}-{nowDate_month}-{nowDate_day}')


def upload_path(instance, filename):
    filetype = 'DVR' if instance.camera_pos else 'DTG'
    if instance.camera_pos:
        return os.path.join(get_date_path(filetype, instance.file_to_oplog.cardata.carnum, instance.file_to_oplog.data_date), instance.camera_pos, filename)
    else:
        return os.path.join(get_date_path(filetype, instance.file_to_oplog.cardata.carnum, instance.file_to_oplog.data_date), filename)

# Create your models here.


class CarDataModel(models.Model):
    cartype = models.CharField(max_length=200, null=True)
    carnum = models.CharField(max_length=200, null=True)
    stack_drive = models.IntegerField(default=0)


class OperationLogModel(models.Model):
    detail = models.TextField(null=True)
    datetimes = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    distance = models.IntegerField(default=0)
    passenger = models.IntegerField(default=0)
    isoweeks = models.IntegerField(default=1)
    cardata = models.ForeignKey(CarDataModel, on_delete=models.PROTECT,
                                related_name='operation', related_query_name="cardata")

    class Meta:
        ordering = ['-created_at']


# class DVRFileModel(ChunkedUpload):
class FileModel(models.Model):
    oplog = models.ForeignKey(OperationLogModel, on_delete=models.CASCADE,
                              related_name='files_to_oplog', related_query_name="oplog_to_file", null=True)
    camera_pos = models.CharField(max_length=4)
    created_at = models.DateTimeField(default=timezone.now, null=True)
    files = models.FileField(upload_to=upload_path, null=True)
    filename = models.CharField(max_length=50, null=True)
    filetype = models.CharField(max_length=10, null=True)
    fileviewsize = models.CharField(max_length=10, null=True)
    filesize = models.IntegerField(null=True)


class DTGDataModel(models.Model):
    oplog = models.ForeignKey(OperationLogModel, on_delete=models.CASCADE,
                              related_name='dtgdatas_to_oplog', related_query_name="oplog_to_dtgdata", null=True)
    dtgfile = models.ForeignKey(FileModel, on_delete=models.CASCADE,
                                related_name='dtgdatas_to_dtgfiles', related_query_name="dtgfile_to_dtgdata", null=True)
    num = models.IntegerField()
    datetimes = models.DateTimeField()
    daily_drive = models.IntegerField()
    stack_drive = models.IntegerField()
    speed = models.IntegerField()
    rpm = models.IntegerField()
    brake_signal = models.IntegerField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    position_angle = models.IntegerField()
    acc_x = models.FloatField()
    acc_y = models.FloatField()
    device_status = models.IntegerField()

    @property
    def location_field_indexing(self):
        return {
            'lat': self.latitude,
            'lon': self.longitude,
        }