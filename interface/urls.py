from django.urls import path
from . import views

app_name = 'interface'
urlpatterns = [
    path('folium/', views.foliums, name='folium'),
    path('mycar/<int:carnumber>', views.foliumsEdit, name='foliumsEdit'),
]
