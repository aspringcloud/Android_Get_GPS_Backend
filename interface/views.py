from django.http.response import JsonResponse
from django.shortcuts import render
from os.path import join
from .models import *
from gps.models import Gps
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

# 폴레니움 맵을 만드는 매소드 : 이걸 기반으로 만들어 지면 그걸 수정하는 방식으로 만들었습니다.
# 만들어진 맵에 붙힌 모듈 : 
# snakeIn : https://github.com/IvanSanchez/Leaflet.Polyline.SnakeAnim
# arrowhead : https://github.com/slutske22/leaflet-arrowheads
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
    return render(request, 'interface/test4.html', context)
    #return JsonResponse(context)

# 데이터를 분 단위로 잘라서 평균낸 퀴리문을 반환해 주는 메소드
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

def getGpsDtaa(gps_datas) :
    return gps_datas\
            .annotate(
            minute=TruncMinute('datetimes')
        ).order_by('minute')\
            .values(
            'minute',
        ).annotate(
            cnt=Count('minute')
        ).annotate(
            avgLongitude=Avg('lat'),
            avgLatitude=Avg('lon'),
            avgSpeed=Avg('speed', output_field=IntegerField()),
        ).values(
            'minute',
            'avgLongitude',
            'avgLatitude',
            'avgSpeed',
        )

# 만들어진 foliums map과 데이터 데이스에서 데이터를 가져와 build를 만들어 주는 부분
def foliumsEdit(request):
    # print(KST)
    KST = datetime.timedelta(hours=9)
    polylineList = []
    FeatureCollection = []
    oplogs = OperationLogModel.objects.filter(id__in=[10]).order_by('datetimes').values(
                'pk',
                'datetimes',
            )
    stamp = 1
    for oplog in oplogs:
        dtg_datas = getDtgData(DTGDataModel.objects.filter(oplog=oplog.get('pk')).exclude(longitude=0,oplog__in=[10,11]).order_by('datetimes'))
        features = []
        location = []
        temp = pd.DataFrame(list(dtg_datas))
        location.append([dtg_datas[0].get('avgLatitude'), dtg_datas[0].get('avgLongitude')] )
        color = f"#{hex(random.randrange(1,16**6))[2:]}"
        for i in range(stamp, len(temp.index)):
            if (i%stamp != 0):
                continue
            location.append([dtg_datas[i].get('avgLatitude'), dtg_datas[i].get('avgLongitude')])
            features.append(
                {
                    "type":"Feature",
                    "geometry":{
                        "type":"LineString",
                        "coordinates": [
                            [dtg_datas[i-stamp].get('avgLongitude'), dtg_datas[i-stamp].get('avgLatitude')],
                            [dtg_datas[i].get('avgLongitude'), dtg_datas[i].get('avgLatitude')],
                        ],
                    },
                    "properties": {
                        "times": [(dtg_datas[i-stamp].get('minute')+KST).strftime('%Y-%m-%dT%H:%M:%S'), (dtg_datas[i].get('minute')+KST).strftime('%Y-%m-%dT%H:%M:%S')],
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
            'color' : color,
            })
        FeatureCollection.append(features)
    context = {
        'polylineList': polylineList,
        # 'FeatureCollection' : {
        #     "type":"FeatureCollection",
        #     'features' : features,
        # } 
        'FeatureCollection' : FeatureCollection,
    }
    return render(request, 'interface/foliumsEdit.html', context)
    # return JsonResponse(context)

# 만들어진 foliums map과 데이터 데이스에서 데이터를 가져와 build를 만들어 주는 부분
def gpsEdit(request):
    KST = datetime.timedelta(hours=9)
    polylineList = []
    FeatureCollection = []
    oplogs = OperationLogModel.objects.filter(id__in=[10,11]).order_by('datetimes').values(
                'pk',
                'datetimes',
            )
    print(oplogs)
    stamp = 1
    for oplog in oplogs:
        dtg_datas = getGpsDtaa(Gps.objects.filter(oplog_id=oplog.get('pk')).order_by('datetimes'))
        features = []
        location = []
        temp = pd.DataFrame(list(dtg_datas))
        location.append([float(dtg_datas[0].get('avgLatitude')), float(dtg_datas[0].get('avgLongitude'))] )
        color = f"#{hex(random.randrange(1,16**6))[2:]}"
        print(temp)
        for i in range(stamp, len(temp.index)):
            if (i%stamp != 0):
                continue
            location.append([float(dtg_datas[i].get('avgLatitude')), float(dtg_datas[i].get('avgLongitude'))])
            features.append(
                {
                    "type":"Feature",
                    "geometry":{
                        "type":"LineString",
                        "coordinates": [
                            [dtg_datas[i-stamp].get('avgLongitude'), dtg_datas[i-stamp].get('avgLatitude')],
                            [dtg_datas[i].get('avgLongitude'), dtg_datas[i].get('avgLatitude')],
                        ],
                    },
                    "properties": {
                        "times": [(dtg_datas[i-stamp].get('minute')+KST).strftime('%Y-%m-%dT%H:%M:%S'), (dtg_datas[i].get('minute')+KST).strftime('%Y-%m-%dT%H:%M:%S')],
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
            'color' : color,
            })
        FeatureCollection.append(features)
    context = {
        'polylineList': polylineList,
        'FeatureCollection' : FeatureCollection,
    }
    #return render(request, 'interface/foliumsEditGps.html', context)
    return JsonResponse(context)

# 또 테스트 하는 부분
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