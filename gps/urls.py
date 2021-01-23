from django.urls import path

from . import views

urlpatterns = [
    path("savegps", views.ActivityGps.as_view()),
    path("gpsinfo", views.GetGpsInfo.as_view()),
]
