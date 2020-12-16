from django.http.response import JsonResponse
from django.shortcuts import render
from os.path import join
from .models import *
from django.db.models import F, Avg, Count, IntegerField, Func
from django.db.models.functions import TruncMinute
from pytz import timezone, utc
from django.conf import settings
import datetime
import pandas as pd
import folium
from folium import plugins
import random
import pprint

KST = timezone('Asia/Seoul')

# Create your views here.
def index(request):
    step = 1
    dtg_datasList = []
    locationList = []
    for oplog in OperationLogModel.objects.all():
        # for oplog in [19,20,24,ß25]:
        dtg_datas = DTGDataModel.objects.filter(oplog=oplog).exclude(longitude=0).order_by('datetimes')\
            .annotate(
            minute=TruncMinute('datetimes')
        ).order_by('minute')\
            .values(
            'minute',
        ).annotate(
            cnt=Count('minute')
        ).annotate(
            avgLongitude=Avg('longitude'),
            avgLatitude=Avg('latitude'),
            avgDailyDrive=Avg('daily_drive', output_field=IntegerField()),
            avgStackDrive=Avg('stack_drive', output_field=IntegerField()),
            avgSpeed=Avg('speed', output_field=IntegerField()),
            avgRpm=Avg('rpm'),
            avgBrakeSignal=Avg('brake_signal'),
            avgPosition_angle=Avg('position_angle'),
            avgAccX=Avg('acc_x'),
            avgAccY=Avg('acc_y'),
            avgDeviceStatus=Avg('device_status'),
        ).values(
            'minute',
            'avgLongitude',
            'avgLatitude',
            'avgDailyDrive',
            'avgStackDrive',
            'avgSpeed',
            'avgRpm',
            'avgBrakeSignal',
            'avgPosition_angle',
            'avgAccX',
            'avgAccY',
            'avgDeviceStatus',
        )
        location = []
        if dtg_datas.count() == 0:
            continue
        dtg_datas = list(dtg_datas)
        dtg_datasList.append(dtg_datas)
        for item in dtg_datas:
            # print(item)
            location.append([item['avgLatitude'], item['avgLongitude']])
        locationList.append(location)
    #     dtg_datas = pd.DataFrame(list(dtg_datas))
    colors = [
        f"{hex(random.randrange(0,16**6))[2:]}" for _ in range(len(locationList))]
    #     for i in range(step, len(dtg_datas.index), step):
    #         folium.Circle(
    #             location = dtg_datas.loc[i, ['avgLatitude','avgLongitude']],
    #             radius = 2,
    #             color = color ,
    #         ).add_to(m)
    #         location.append(dtg_datas.loc[i, ['avgLatitude','avgLongitude']])
    #     if location :
    #         polyline = folium.PolyLine(location,
    #                 weight=2,
    #                 opacity=0.8,
    #                 color = color ,
    #                 )
    #         polyline.add_to(m)
    # # https://github.com/slutske22/leaflet-arrowheads
    # m.save(join(settings.BASE_DIR, 'mapDir', 'map.html'))
    # print(dtg_datasList)
    # print(locationList)
    context = {
        'dtg_datasList': dtg_datasList,
        'locationList': locationList,
        'colors': colors,
    }
    # return render(request, 'interface/fatosmap.html', context)
    return render(request, 'interface/map2.html', context)
    # return JsonResponse(context)


def get_json(request):
    step = 1
    operationLogList = []
    locationList = []
    oplogs = OperationLogModel.objects.all().values(
                'pk',
                'detail',
                'datetimes',
                'created_at',
                'distance',
                'passenger',
                'isoweeks',
            )
    for oplog in oplogs:
        # for oplog in [19,20,24,ß25]:
        dtg_datas = getDtgData(oplog)
        location = []
        for item in dtg_datas:
            # print(item)
            location.append([item['avgLatitude'], item['avgLongitude']])
        locationList.append(location)
        if dtg_datas.count() == 0:
            continue
        dtg_datas = list(dtg_datas)
        oplog['dtg_datas'] = dtg_datas
        operationLogList.append(oplog)

    colors = [f"{hex(random.randrange(1,16**6))[2:]}" for _ in range(len(locationList))]
    
    context = {
        'operationLogList' : operationLogList,
        'locationList': locationList,
        'colors': colors,
    }
    return render(request, 'interface/test4.html', context)
    # return JsonResponse(context)


def foliums(request):
    m = folium.Map(
        location=[36.50070878260868, 127.26875695652177],
        zoom_start=20
    )
    step = 1
    dtg_datasList = []
    locationList = []
    oplogs = OperationLogModel.objects.filter(pk=1).order_by('datetimes').values(
                'pk',
                'detail',
                'datetimes',
                'created_at',
                'distance',
                'passenger',
                'isoweeks',
            )
    lines = []
    stamp = 10
    weight = 7
    for oplog in oplogs:
        # for oplog in [19,20,24,ß25]:
        fg = folium.FeatureGroup(name=f"{oplog.get('datetimes').strftime('%Y-%m-%d')}")
        m.add_child(fg)
        dtg_datas = DTGDataModel.objects.filter(oplog=oplog.get('pk')).exclude(longitude=0).order_by('datetimes').values('latitude','longitude','datetimes')
        if dtg_datas.count() == 0:
            continue
        location = []
        temp = pd.DataFrame(list(dtg_datas))
        location.append(temp.loc[0, ['latitude', 'longitude']])
        color = f"#{hex(random.randrange(1,16**6))[2:]}"
        for i in range(stamp, len(temp.index)):
            if (i%stamp != 0):
                continue
            location.append(temp.loc[i, ['latitude','longitude']])
            lines.append(
                {
                    "coordinates": [
                        [dtg_datas[i-stamp].get('longitude'), dtg_datas[i-stamp].get('latitude')],
                        [dtg_datas[i].get('longitude'), dtg_datas[i].get('latitude')],
                    ],
                    "dates": [dtg_datas[i-stamp].get('datetimes').strftime('%Y-%m-%dT%H:%M:%S'), dtg_datas[i].get('datetimes').strftime('%Y-%m-%dT%H:%M:%S')],
                    # "color": "red",
                }
            )
            # folium.Circle(
            #     location = temp.loc[i, ['latitude','longitude']],
            #     color = color,
            #     radius = 2,
            # ).add_to(fg)
        if location :
            polyline = folium.PolyLine(location,
                    weight = weight,
                    color = color,
                    # opacity=0.8,
                )
            polyline.add_to(fg)
    # https://github.com/slutske22/leaflet-arrowheads
    folium.LayerControl(collapsed=False).add_to(m)

    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": line["coordinates"],
            },
            "properties": {
                "times": line["dates"],
                "style": {
                    # "color": line["color"],
                    "weight": line["weight"] if "weight" in line else weight,
                    "strokeColor" : 'black',
                    "strokeOpacity" : 1.0,
                    "strokeWeight" : 4,
                    "opacity" : 1,
                },
            },
        }
        for line in lines
    ]
    plugins.TimestampedGeoJson(
        {
            "type": "FeatureCollection",
            "features": features,
        },
        period="PT1S",
        auto_play=False,
        loop=False,
        # max_speed=1,
        duration=f'PT{stamp}S',
        time_slider_drag_update=True,
    ).add_to(m)

    m.save(join(settings.BASE_DIR, 'mapDir', 'map2.html'))
    context = {
        # 'operationLogList' : operationLogList,
        'locationList': locationList,
        'lines' : lines
    }
    # return render(request, 'interface/test4.html', context)
    return JsonResponse(context)



def getDtgData(dtg_datas) :
    return dtg_datas\
            .annotate(
            minute=TruncMinute('datetimes')
        ).order_by('minute')\
            .values(
            'minute',
        ).annotate(
            cnt=Count('minute')
        ).annotate(
            avgLongitude=Avg('longitude'),
            avgLatitude=Avg('latitude'),
            avgDailyDrive=Avg('daily_drive', output_field=IntegerField()),
            avgStackDrive=Avg('stack_drive', output_field=IntegerField()),
            avgSpeed=Avg('speed', output_field=IntegerField()),
            avgRpm=Avg('rpm'),
            avgBrakeSignal=Avg('brake_signal'),
            avgPosition_angle=Avg('position_angle'),
            avgAccX=Avg('acc_x'),
            avgAccY=Avg('acc_y'),
            avgDeviceStatus=Avg('device_status'),
        ).values(
            'minute',
            'avgLongitude',
            'avgLatitude',
            'avgDailyDrive',
            'avgStackDrive',
            'avgSpeed',
            'avgRpm',
            'avgBrakeSignal',
            'avgPosition_angle',
            'avgAccX',
            'avgAccY',
            'avgDeviceStatus',
        )


def foliumsEdit(request):
    KST = datetime.timedelta(hours=9)
    polylineList = []
    oplogs = OperationLogModel.objects.all().order_by('datetimes').values(
                'pk',
                'detail',
                'datetimes',
                'created_at',
                'distance',
                'passenger',
                'isoweeks',
            )
    features = []
    stamp = 10
    for oplog in oplogs:
        
        dtg_datas = DTGDataModel.objects.filter(oplog=oplog.get('pk')).exclude(longitude=0).order_by('datetimes').values('latitude','longitude','datetimes')
        if dtg_datas.count() == 0:
            continue
        location = []
        temp = pd.DataFrame(list(dtg_datas))
        location.append([dtg_datas[0].get('latitude'), dtg_datas[0].get('longitude')] )
        color = f"#{hex(random.randrange(1,16**6))[2:]}"
        for i in range(stamp, len(temp.index)):
            if (i%stamp != 0):
                continue
            location.append([dtg_datas[i].get('latitude'), dtg_datas[i].get('longitude')])
            features.append(
                {
                    "type":"Feature",
                    "geometry":{
                        "type":"LineString",
                        "coordinates": [
                            [dtg_datas[i-stamp].get('longitude'), dtg_datas[i-stamp].get('latitude')],
                            [dtg_datas[i].get('longitude'), dtg_datas[i].get('latitude')],
                        ],
                    },
                    "properties": {
                        "times": [(dtg_datas[i-stamp].get('datetimes')+KST).strftime('%Y-%m-%dT%H:%M:%S'), (dtg_datas[i].get('datetimes')+KST).strftime('%Y-%m-%dT%H:%M:%S')],
                        "style":{
                            "weight":7,
                            "strokeColor":"black",
                            "strokeOpacity":1.0,
                            "strokeWeight":4,
                            "opacity":1,
                            "colors":color,
                        }
                    }
                }
            )
        polylineList.append({
            'oplog' : oplog,
            'poltline' : location,
            'color' : color
            })
    context = {
        'polylineList': polylineList,
        'FeatureCollection' : {
            "type":"FeatureCollection",
            'features' : features,
        } 
    }
    return render(request, 'interface/foliumsEdit.html', context)
    # return JsonResponse(context)


def getData(request):
    KST = datetime.timedelta(hours=9)
    polylineList = []
    oplogs = OperationLogModel.objects.all().order_by('datetimes').values(
                'pk',
                'detail',
                'datetimes',
                'created_at',
                'distance',
                'passenger',
                'isoweeks',
            )
    features = []
    stamp = 10
    print(oplogs.query)
    for oplog in oplogs:
        dtg_datas = DTGDataModel.objects.filter(oplog=oplog.get('pk')).exclude(longitude=0).order_by('datetimes').values('latitude','longitude','datetimes')
        if dtg_datas.count() == 0:
            continue
        location = []
        
        temp = pd.DataFrame(list(dtg_datas))
        location.append([dtg_datas[0].get('latitude'), dtg_datas[0].get('longitude')] )
        color = f"#{hex(random.randrange(1,16**6))[2:]}"
        for i in range(stamp, len(temp.index)):
            if (i%stamp != 0):
                continue
            location.append([dtg_datas[i].get('latitude'), dtg_datas[i].get('longitude')])
            features.append(
                {
                    "type":"Feature",
                    "geometry":{
                        "type":"LineString",
                        "coordinates": [
                            [dtg_datas[i-stamp].get('longitude'), dtg_datas[i-stamp].get('latitude')],
                            [dtg_datas[i].get('longitude'), dtg_datas[i].get('latitude')],
                        ],
                    },
                    "properties": {
                        "times": [(dtg_datas[i-stamp].get('datetimes')+KST).strftime('%Y-%m-%dT%H:%M:%S'), (dtg_datas[i].get('datetimes')+KST).strftime('%Y-%m-%dT%H:%M:%S')],
                        "style":{
                            "weight":7,
                            "strokeColor":"black",
                            "strokeOpacity":1.0,
                            "strokeWeight":4,
                            "opacity":1,
                            "colors":color,
                        }
                    }
                }
            )
        polylineList.append({
            'oplog' : oplog,
            'poltline' : location,
            'color' : color
            })
    context = {
        'polylineList': polylineList,
        'FeatureCollection' : {
            "type":"FeatureCollection",
            'features' : features,
        } 
    }
    # return render(request, 'interface/foliumsEdit.html', context)
    return JsonResponse(context)