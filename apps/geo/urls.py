from django.urls import path

from . import views

app_name = 'geo'

urlpatterns = [
    path('', views.BranchMapView.as_view(), name='branches'),
    path('<slug:slug>/', views.CityBranchListView.as_view(), name='city_branches'),
]
