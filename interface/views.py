from django.shortcuts import render, HttpResponse
from .models import *

# Create your views here.
def index(request):
    dtg_datas = DTGDataModel.objects.filter(oplog = 20).order_by('datetimes')

    context = {
        'dtg_datas' : dtg_datas,
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

def test(request):
    cardatas = CarDataModel.objects.all()
    dtg_datas = []
    for cardata in cardatas:
        now_operations = OperationLogModel.objects.filter(cardata = cardata).first()
        dtg_datas.append(DTGDataModel.objects.filter(oplog = now_operations).order_by('datetimes'))
    context = {
        'dtg_datas' : dtg_datas,
    }
    return render(request, 'interface/test.html', context)