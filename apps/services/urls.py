from django.urls import path

from apps.services import views

app_name = 'services'

urlpatterns = [
    path('additional/', views.AdditionalServiceListView.as_view(), name='additional'),
    path('tariffs/', views.TariffListView.as_view(), name='tariffs'),
    path('', views.ServiceCategoryListView.as_view(), name='list'),
    path('<slug:slug>/', views.ServiceCategoryDetailView.as_view(), name='category'),
    path('<slug:category_slug>/<slug:slug>/', views.ServiceDetailView.as_view(), name='detail'),
]
