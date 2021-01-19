import json
import datetime
from django.utils import timezone

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from . import models
from interface.models import DTGDataModel, Legend, CarDataModel
from accounts.models import User

class ActivityGps(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            print(data)
            if data['activty'] == "True":
                now = datetime.datetime.now()
                try:
                    legend = Legend.objects.get(datetimes__startswith=datetime.date(now.year,now.month,now.day))
                except Legend.DoesNotExist:
                    legend = Legend.objects.create(
                        detail="SmartPhone GPS ADD",
                        cardata_id = CarDataModel.objects.get(pk=1).id,
                    )
                    print(legend.id)

                gps = DTGDataModel.objects.create(
                    latitude = float(data['lat'])  ,
                    longitude = float(data['lon']) ,
                    Legend=Legend.objects.get(id=legend.id),
                    speed = 0,
                    num = 0 ,
                    stack_drive = 0 ,
                    daily_drive = 0,
                    rpm = 0 ,
                    brake_signal = 0 ,
                    position_angle = 0 ,
                    device_status = 0 ,
                    acc_x = 0.0 ,
                    acc_y = 0.0 ,
                )
                
                return JsonResponse({"activty" : True}, status = 200)
            else :
                return JsonResponse({"activty" : False}, status = 200)

        except ValueError as v:
            print(v)
            return JsonResponse({"error" : "ValueError"}, status = 400)
        except TypeError as t:
            print(t)
            return JsonResponse({"error" : "TypeError"}, status = 400)

    def get(self, request):
        gps = models.Gps.objects.all()

        data = [{
            "id"      : g.id ,
            "lat"     : g.lat ,
            "lon"     : g.lon ,
            "speed"   : g.speed ,
            "datetimes" : g.datetimes ,
        } for g in gps]

        return JsonResponse(data, safe=False,status=200)