from django.urls import path
from . import views

app_name = 'interface'
urlpatterns = [
    path('folium/', views.foliums, name='folium'),
    path('foliumsEdit/', views.foliumsEdit, name='foliumsEdit'),
    path('foliumsEditGps/', views.gpsEdit, name='foliumsEditGps'),
    path('getData/', views.getData, name='getData'),
    # path('test2/', views.test2, name='test2'),
    # path('test3/', views.test3, name='test3'),
    # path('getnow/', views.get_realtime, name='get_realtime'),
]
