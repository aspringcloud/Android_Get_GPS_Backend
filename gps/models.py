from django.db import models
from interface.models import OperationLogModel


class Gps(models.Model):
    lat = models.DecimalField(max_digits=20, decimal_places=15, default=0)
    lon = models.DecimalField(max_digits=20, decimal_places=15, default=0)
    speed = models.DecimalField(max_digits=20, decimal_places=15, default=0)
    datetimes = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "gps_info"

    def __str__(self):
        return self.lat 
