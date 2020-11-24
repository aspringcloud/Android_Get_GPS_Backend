from django.http.response import JsonResponse
from django.shortcuts import render
from .models import *
from django.db.models import F
import datetime
from pytz import timezone, utc
import pprint

KST = timezone('Asia/Seoul')

# Create your views here.


def index(request):
    dtg_datas = DTGDataModel.objects.filter(oplog=20).order_by('datetimes')

    context = {
        'dtg_datas': dtg_datas,
    }
    # output = []
    # response = HttpResponse (content_type='text/csv')
    # writer = csv.writer(response)
    # query_set = DTGDataModel.objects.filter(oplog = 1).order_by('num')
    # #Header
    # writer.writerow(['num',
    #     'datetimes',
    #     'daily_drive',
    #     'stack_drive',
    #     'speed',
    #     'rpm',
    #     'brake_signal',
    #     'longitude',
    #     'latitude',
    #     'position_angle',
    #     'acc_x',
    #     'acc_y',
    #     'device_status'])
    # for item in query_set:
    #     output.append([item.num,
    #         item.datetimes,
    #         item.daily_drive,
    #         item.stack_drive,
    #         item.speed,
    #         item.rpm,
    #         item.brake_signal,
    #         item.longitude,
    #         item.latitude,
    #         item.position_angle,
    #         item.acc_x,
    #         item.acc_y,
    #         item.device_status])
    # #CSV Data
    # writer.writerows(output)
    # return response
    return render(request, 'interface/test.html', context)


def test2(request):
    cardatas = CarDataModel.objects.all()
    context = {}
    context[cardatas] = cardatas
    for cardata in cardatas:
        now_operations = OperationLogModel.objects.filter(
            cardata=cardata).order_by('datetimes').first()
        context[f'{cardata.carnum}_data'] = DTGDataModel.objects.filter(
            oplog=now_operations).annotate(carnum=F('oplog__cardata__carnum')).order_by('datetimes')
    # print(context)
    return render(request, 'interface/test2.html', context)


def test3(request):
    context = {}
    return render(request, 'interface/test3.html', context)


def get_realtime(request):
    now = datetime.datetime.utcnow()
    kst_time = utc.localize(now).astimezone(KST)
    one_second = datetime.timedelta(seconds=1)
    cardatas = CarDataModel.objects.all().values('cartype', 'carnum', 'stack_drive')
    get_now_data = DTGDataModel.objects.filter(datetimes__range=(
        kst_time - one_second, kst_time + one_second)).annotate(carnum=F('oplog__cardata__carnum'))
    # get_now_data = DTGDataModel.objects.all().annotate(carnum = F('oplog__cardata__carnum'))
    # print(get_now_data[0].__dict__)
    result = {}
    result['cardatas'] = list(cardatas)
    for cardata in cardatas:
        # print(cardata['carnum'])
        result[f'{cardata["carnum"]}_data'] = list(get_now_data.filter(carnum=cardata['carnum']).
                                                   values('num', 'datetimes', 'daily_drive', 'stack_drive', 'speed', 'rpm', 'brake_signal', 'longitude', 'latitude', 'position_angle', 'acc_x', 'acc_y', 'device_status',))
    return JsonResponse(result)
