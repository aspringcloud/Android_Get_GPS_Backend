import json
import datetime

from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from .models import Gps
from interface.models import DTGDataModel, Legend, CarDataModel, CarDataModel
from accounts.models import User

class ActivityGps(View):
    def post(self, request):
        try:
            KST = datetime.timedelta(hours=9)
            data = json.loads(request.body)
            print(data)
            now = timezone.now()
            
            try:
                car = CarDataModel.objects.get(carnum=int(data["car"]))
                legend = Legend.objects.get(datetimes__startswith=datetime.date(now.year,now.month,now.day),car_id=car.id)

            except Legend.DoesNotExist:
                legend = Legend.objects.create(
                    detail     = "SmartPhone GPS ADD",
                    car_id = car.id,
                )

            DTGDataModel.objects.create(
                latitude       = float(data['lat'])  ,
                longitude      = float(data['lon']) ,
                Legend         = Legend.objects.get(id=legend.id),
                speed          = int(float(data['speed'])),
                num            = 0 ,
                stack_drive    = 0 ,
                daily_drive    = 0 ,
                rpm            = 0 ,
                brake_signal   = 0 ,
                position_angle = 0 ,
                device_status  = 0 ,
                acc_x          = 0.0 ,
                acc_y          = 0.0 ,
            )
            if data['filesize'] != 0:
                legend.filesize = int(data['filesize'])
                legend.save()

            return JsonResponse({"activty" : True}, status = 200)

        except Exception as e:
            print(e)
            return JsonResponse({"error" : e}, status = 400)

class GetGpsInfo(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            now = datetime.datetime.now()
            car = CarDataModel.objects.get(carnum=int(data['carnumber']))
            legend = Legend.objects.get(datetimes__startswith=datetime.date(now.year,now.month,now.day),car_id=car.id)

            return JsonResponse({"filesize" : legend.filesize},status=200)

        except Legend.DoesNotExist:
            return JsonResponse({"filesize" : 0}, status=200)
        except Exception as e:
            return JsonResponse({"Error" : "Error 400"}, status=400)
