import json

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from . import models

class ActivityGps(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            print(data)
            if data['activty'] == "True":
                gps = models.Gps.objects.create(
                    lat   = float(data['lat'])   ,
                    lon   = float(data['lon'])   ,
                    speed   = float(data['speed'])   ,
                )
                return JsonResponse({"activty" : True}, status = 200)
            else :
                return JsonResponse({"activty" : False}, status = 200)

        except ValueError:
            return JsonResponse({"error" : "ValueError"}, status = 400)
        except TypeError:
            return JsonResponse({"error" : "TypeError"}, status = 400)

    def get(self, request):
        gps = models.Gps.objects.all()

        data = [{
            "id"      : g.id ,
            "lat"     : g.lat ,
            "lon"     : g.lon ,
            "activty" : True,
        } for g in gps[:100]]

        return JsonResponse(data, safe=False,status=200)