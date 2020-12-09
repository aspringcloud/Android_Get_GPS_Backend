from django.http.response import JsonResponse
from django.shortcuts import render
from os.path import join
from .models import *
from django.db.models import F, Avg, Count, IntegerField, Func
from django.db.models.functions import TruncMinute
from pytz import timezone, utc
from django.conf import settings
import pandas as pd
import folium
from folium import plugins
import random
import pprint

KST = timezone('Asia/Seoul')

# Create your views here.


# def index(request):
#     dtg_datas = DTGDataModel.objects.filter(oplog=20).order_by('datetimes')

#     context = {
#         'dtg_datas': dtg_datas,
#     }
#     # output = []
#     # response = HttpResponse (content_type='text/csv')
#     # writer = csv.writer(response)
#     # query_set = DTGDataModel.objects.filter(oplog = 1).order_by('num')
#     # #Header
#     # writer.writerow(['num',
#     #     'datetimes',
#     #     'daily_drive',
#     #     'stack_drive',
#     #     'speed',
#     #     'rpm',
#     #     'brake_signal',
#     #     'longitude',
#     #     'latitude',
#     #     'position_angle',
#     #     'acc_x',
#     #     'acc_y',
#     #     'device_status'])
#     # for item in query_set:
#     #     output.append([item.num,
#     #         item.datetimes,
#     #         item.daily_drive,
#     #         item.stack_drive,
#     #         item.speed,
#     #         item.rpm,
#     #         item.brake_signal,
#     #         item.longitude,
#     #         item.latitude,
#     #         item.position_angle,
#     #         item.acc_x,
#     #         item.acc_y,
#     #         item.device_status])
#     # #CSV Data
#     # writer.writerows(output)
#     # return response
#     return render(request, 'interface/test.html', context)


# def test2(request):
#     cardatas = CarDataModel.objects.all()
#     context = {}
#     context[cardatas] = cardatas
#     for cardata in cardatas:
#         now_operations = OperationLogModel.objects.filter(
#             cardata=cardata).order_by('datetimes').first()
#         context[f'{cardata.carnum}_data'] = DTGDataModel.objects.filter(
#             oplog=now_operations).annotate(carnum=F('oplog__cardata__carnum')).order_by('datetimes')
#     # print(context)
#     return render(request, 'interface/test2.html', context)


# def test3(request):
#     context = {}
#     return render(request, 'interface/test3.html', context)


# def get_realtime(request):
#     now = datetime.datetime.utcnow()
#     kst_time = utc.localize(now).astimezone(KST)
#     one_second = datetime.timedelta(seconds=1)
#     cardatas = CarDataModel.objects.all().values('cartype', 'carnum', 'stack_drive')
#     get_now_data = DTGDataModel.objects.filter(datetimes__range=(
#         kst_time - one_second, kst_time + one_second)).annotate(carnum=F('oplog__cardata__carnum'))
#     # get_now_data = DTGDataModel.objects.all().annotate(carnum = F('oplog__cardata__carnum'))
#     # print(get_now_data[0].__dict__)
#     result = {}
#     result['cardatas'] = list(cardatas)
#     for cardata in cardatas:
#         # print(cardata['carnum'])
#         result[f'{cardata["carnum"]}_data'] = list(get_now_data.filter(carnum=cardata['carnum']).
#                                                    values('num', 'datetimes', 'daily_drive', 'stack_drive', 'speed', 'rpm', 'brake_signal', 'longitude', 'latitude', 'position_angle', 'acc_x', 'acc_y', 'device_status',))
#     return JsonResponse(result)


def index(request):
    step = 1
    # m = folium.Map(
    #         location=['36.727931', '127.442758'],
    #         zoom_start=20
    #     )
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
    return render(request, 'interface/test3.html', context)
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
    oplogs = OperationLogModel.objects.all().values(
                'pk',
                'detail',
                'datetimes',
                'created_at',
                'distance',
                'passenger',
                'isoweeks',
            )
    lines = []
    for oplog in oplogs:
        # for oplog in [19,20,24,ß25]:
        fg = folium.FeatureGroup(name=f"{oplog.get('datetimes')}")
        m.add_child(fg)
        dtg_datas = DTGDataModel.objects.filter(oplog=oplog.get('pk')).exclude(longitude=0).order_by('datetimes').values('latitude','longitude','datetimes')
        if dtg_datas.count() == 0:
            continue
        location = []
        temp = pd.DataFrame(list(dtg_datas))
        # print(temp)
        location.append(temp.loc[0, ['latitude','longitude']])
        for i in range(1, len(temp.index)):
            # location.append([item.longitude, item.latitude])
            # print(temp.loc[i, ['latitude','longitude']])
            location.append(temp.loc[i, ['latitude','longitude']])
            lines.append(
            {
                "coordinates": [
                    temp.loc[i-1, ['latitude','longitude']],
                    temp.loc[i, ['latitude','longitude']],
                ],
                "dates": [temp.loc[i-1, ['datetimes']], temp.loc[i, ['datetimes']]],
                "color": "red",
            })
        # print(location)
        dtg_datas = getDtgData(dtg_datas)
        dtg_datas = list(dtg_datas)
        dtg_datas = pd.DataFrame(list(dtg_datas))
        color = f"#{hex(random.randrange(1,16**6))[2:]}"
        for i in range(step, len(dtg_datas.index), step):
            folium.Circle(
                location = dtg_datas.loc[i, ['avgLatitude','avgLongitude']],
                color = color,
                radius = 2,
            ).add_to(fg)
        if location :
            polyline = folium.PolyLine(location,
                    weight=2,
                    color = color,
                    opacity=0.8,
                )
            polyline.add_to(fg)
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
                        "color": line["color"],
                        # "weight": line["weight"] if "weight" in line else 5,
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
        period="PT1M",
        add_last_point=True,
    ).add_to(m)
    # https://github.com/slutske22/leaflet-arrowheads
    folium.LayerControl(collapsed=False).add_to(m)
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