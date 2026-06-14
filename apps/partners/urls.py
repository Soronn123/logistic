from django.urls import path

from . import views

app_name = 'partners'

urlpatterns = [
    path('', views.PartnerOverviewView.as_view(), name='overview'),
    path('apply/', views.PartnerApplyView.as_view(), name='apply'),
    path('list/', views.PartnerListView.as_view(), name='list'),
    path('iframe/', views.IframeModulesView.as_view(), name='iframe'),
    path('banners/', views.PartnerBannersView.as_view(), name='banners'),
    path('cards/', views.partner_cards_partial, name='cards'),
]
